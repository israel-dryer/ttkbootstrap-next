from __future__ import annotations

import csv
import re
from collections.abc import Sequence
from typing import Any, Dict, List, Optional, Union, Mapping, Iterable, Tuple

try:
    # keep your import to avoid touching callers
    from ttkbootstrap_next.types import Primitive  # type: ignore
except Exception:
    Primitive = Any  # fallback


class MemoryDataSource:
    """
    Pure-Python in-memory data manager with pagination, sorting, filtering,
    inferred schema, and full CRUD support.

    Filtering:
        set_filter("selected = 1 AND score >= 90")
        Supported ops: =, !=, >, >=, <, <=, CONTAINS, STARTSWITH, ENDSWITH, IN, LIKE
        - Strings: quoted ('foo' or "foo")
        - Numbers: 42, 3.14
        - Booleans: true/false
        - None: null
        - IN: comma-separated list: "status IN ('new','open')"
        - LIKE: % and _ wildcards (SQL-ish)

    Sorting:
        set_sort("last_name ASC, score DESC")
        ASC is default if omitted.

    Notes:
        - Records are dictionaries. If you pass primitives, they'll be wrapped as {"text": str(x)}.
        - Ensures an integer `id` field and an integer `selected` field (0/1).
    """

    def __init__(self, page_size: int = 10):
        self.page_size = page_size
        self._table = "records"
        self._page = 0
        self._columns: List[str] = []
        self._data: List[Dict[str, Any]] = []  # authoritative store
        self._id_index: Dict[Any, int] = {}  # id -> list index
        self._where_sql: str = ""
        self._order_by_sql: str = ""
        self._filter_predicate = None  # callable | None
        self._sort_keys: List[Tuple[str, bool]] = []  # (col, reverse)

    # ----------------------------
    # Internal helpers
    # ----------------------------

    @staticmethod
    def _infer_type(value: Any) -> str:
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, (bytes, bytearray)):
            return "BLOB"
        return "TEXT"

    @staticmethod
    def _is_mapping(x: Any) -> bool:
        return isinstance(x, Mapping)

    def _rebuild_id_index(self) -> None:
        self._id_index.clear()
        for i, rec in enumerate(self._data):
            self._id_index[rec.get("id")] = i

    def _ensure_selected_column(self) -> None:
        if "selected" not in self._columns:
            self._columns.append("selected")
            for r in self._data:
                r.setdefault("selected", 0)

    def _ensure_id(self) -> None:
        # make sure ids are unique & ints; assign incrementally if missing
        used = set()
        max_id = 0
        for r in self._data:
            if "id" in r and isinstance(r["id"], int):
                used.add(r["id"])
                max_id = max(max_id, r["id"])
        for r in self._data:
            if "id" not in r or not isinstance(r["id"], int) or r["id"] in used:
                max_id += 1
                r["id"] = max_id
                used.add(max_id)
        self._rebuild_id_index()

    @staticmethod
    def _coerce_literal(s: str) -> Any:
        """Coerce a string token to Python literal (int/float/bool/None/str)."""
        t = s.strip()
        # quoted string
        if (len(t) >= 2 and ((t[0] == t[-1] == "'") or (t[0] == t[-1] == '"'))):
            return t[1:-1]
        # booleans
        if t.lower() == "true":
            return True
        if t.lower() == "false":
            return False
        # null
        if t.lower() in ("null", "none"):
            return None
        # int
        try:
            return int(t)
        except Exception:
            pass
        # float
        try:
            return float(t)
        except Exception:
            pass
        # raw string
        return t

    @staticmethod
    def _like_to_regex(pattern: str) -> re.Pattern:
        # SQL LIKE: % -> .*, _ -> .
        # Escape regex special chars first, then replace placeholders.
        esc = ""
        for ch in pattern:
            if ch in ".^$*+?{}[]\\|()":
                esc += "\\" + ch
            else:
                esc += ch
        esc = esc.replace("%", ".*").replace("_", ".")
        return re.compile("^" + esc + "$", re.IGNORECASE)

    def _parse_filter(self, where_sql: str):
        """
        Very small safe parser that supports AND/OR and the ops noted in the docstring.
        Grammar (simplified):
            expr := term ( (AND|OR) term )*
            term := ident OP value
            OP   := = | != | > | >= | < | <= | CONTAINS | STARTSWITH | ENDSWITH | IN | LIKE
            value for IN := '(' v1, v2, ... ')'
        """
        if not where_sql:
            return None

        # Split on AND/OR while preserving them; naive but practical.
        tokens = re.split(r"\s+(AND|OR)\s+", where_sql, flags=re.IGNORECASE)
        # tokens like: [term, 'AND', term, 'OR', term, ...]
        terms: List[Tuple[str, str, Any]] = []
        ops_between: List[str] = []

        def parse_term(t: str) -> Tuple[str, str, Any]:
            # Match IN list specially
            m_in = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+IN\s*\((.*)\)\s*$", t, flags=re.IGNORECASE)
            if m_in:
                col, inner = m_in.group(1), m_in.group(2)
                parts = [p.strip() for p in inner.split(",") if p.strip()]
                values = [self._coerce_literal(p) for p in parts]
                return col, "IN", values

            # Match LIKE
            m_like = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+LIKE\s+(.+)\s*$", t, flags=re.IGNORECASE)
            if m_like:
                col, val = m_like.group(1), self._coerce_literal(m_like.group(2))
                return col, "LIKE", val

            # Match wordy ops
            for op in ("CONTAINS", "STARTSWITH", "ENDSWITH"):
                m = re.match(rf"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+{op}\s+(.+)\s*$", t, flags=re.IGNORECASE)
                if m:
                    col, val = m.group(1), self._coerce_literal(m.group(2))
                    return col, op.upper(), val

            # Match symbolic ops
            m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(=|!=|>=|>|<=|<)\s*(.+)\s*$", t)
            if m:
                col, op, val = m.group(1), m.group(2), self._coerce_literal(m.group(3))
                return col, op, val

            # Fallback: treat as "truthy" column exists
            m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*$", t)
            if m:
                col = m.group(1)
                return col, "truthy", True

            raise ValueError(f"Unrecognized filter term: {t!r}")

        for i, tok in enumerate(tokens):
            if i % 2 == 0:  # term
                if not tok.strip():
                    continue
                terms.append(parse_term(tok))
            else:  # AND/OR
                ops_between.append(tok.strip().upper())

        if not terms:
            return None

        # Prepare LIKE regex ahead of time
        prepared: List[Tuple[str, str, Any]] = []
        for col, op, val in terms:
            if op == "LIKE" and isinstance(val, str):
                prepared.append((col, op, self._like_to_regex(val)))
            else:
                prepared.append((col, op, val))

        def predicate(row: Mapping[str, Any]) -> bool:
            def eval_term(col: str, op: str, val: Any) -> bool:
                rv = row.get(col, None)
                try:
                    if op == "=":   return rv == val
                    if op == "!=":  return rv != val
                    if op == ">":   return (rv is not None) and (val is not None) and rv > val
                    if op == ">=":  return (rv is not None) and (val is not None) and rv >= val
                    if op == "<":   return (rv is not None) and (val is not None) and rv < val
                    if op == "<=":  return (rv is not None) and (val is not None) and rv <= val
                    if op == "CONTAINS":
                        return (rv is not None) and (val is not None) and (str(val).lower() in str(rv).lower())
                    if op == "STARTSWITH":
                        return (rv is not None) and (val is not None) and str(rv).lower().startswith(str(val).lower())
                    if op == "ENDSWITH":
                        return (rv is not None) and (val is not None) and str(rv).lower().endswith(str(val).lower())
                    if op == "IN":
                        return rv in val
                    if op == "LIKE" and isinstance(val, re.Pattern):
                        return (rv is not None) and bool(val.match(str(rv)))
                    if op == "truthy":
                        return bool(rv)
                except Exception:
                    return False
                return False

            # Evaluate with AND/OR left-to-right
            result = eval_term(*prepared[0])
            for j, t in enumerate(prepared[1:], start=0):
                op_between = ops_between[j] if j < len(ops_between) else "AND"
                if op_between == "AND":
                    result = result and eval_term(*t)
                else:
                    result = result or eval_term(*t)
            return result

        return predicate

    def _parse_sort(self, order_by_sql: str) -> List[Tuple[str, bool]]:
        """
        Parse "col ASC, other DESC" into [(col, reverse_bool), ...]
        """
        if not order_by_sql:
            return []
        parts = [p.strip() for p in order_by_sql.split(",") if p.strip()]
        out: List[Tuple[str, bool]] = []
        for p in parts:
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)(?:\s+(ASC|DESC))?$", p, flags=re.IGNORECASE)
            if not m:
                continue
            col = m.group(1)
            dir_tok = (m.group(2) or "ASC").upper()
            out.append((col, dir_tok == "DESC"))
        return out

    def _apply_filter_and_sort(self, rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # filter
        if self._filter_predicate:
            rows = [r for r in rows if self._filter_predicate(r)]
        else:
            rows = list(rows)

        # sort (stable, multi-key)
        if self._sort_keys:
            def key_func(r: Dict[str, Any]):
                key_parts = []
                for col, reverse in self._sort_keys:
                    v = r.get(col)
                    # Normalize None to sort consistently (None last for ASC)
                    # We'll handle reverse by sorting per-key in passes
                    key_parts.append((v is None, v))
                return tuple(key_parts)

            # To respect per-column ASC/DESC, apply keys in reverse order
            for col, rev in reversed(self._sort_keys):
                rows.sort(key=lambda r, c=col: (r.get(c) is None, r.get(c)), reverse=rev)

        return rows

    # ----------------------------
    # Public API (mirrors original)
    # ----------------------------

    def set_data(self, records: Union[Sequence[Primitive], Sequence[Dict[str, Any]]]):
        if not records:
            self._data = []
            self._columns = []
            self._rebuild_id_index()
            return self

        # Coerce primitives to dicts
        if records and not self._is_mapping(records[0]):
            records = [dict(text=str(x)) for x in records]  # type: ignore

        # ensure id & selected
        data: List[Dict[str, Any]] = []
        for i, rec in enumerate(records):  # type: ignore
            r = dict(rec)
            r.setdefault("id", i)
            r.setdefault("selected", 0)
            data.append(r)

        self._data = data
        self._columns = list(self._data[0].keys())
        self._ensure_id()
        self._ensure_selected_column()
        return self

    def set_filter(self, where_sql: str = ""):
        self._where_sql = where_sql or ""
        self._filter_predicate = self._parse_filter(self._where_sql)

    def set_sort(self, order_by_sql: str = ""):
        self._order_by_sql = order_by_sql or ""
        self._sort_keys = self._parse_sort(self._order_by_sql)

    def _filtered_sorted_rows(self) -> List[Dict[str, Any]]:
        return self._apply_filter_and_sort(self._data)

    def get_page(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        if page is not None:
            self._page = max(0, int(page))
        rows = self._filtered_sorted_rows()
        start = self._page * self.page_size
        end = start + self.page_size
        return [dict(r) for r in rows[start:end]]

    def next_page(self) -> List[Dict[str, Any]]:
        if self.has_next_page():
            self._page += 1
        return self.get_page()

    def prev_page(self) -> List[Dict[str, Any]]:
        self._page = max(0, self._page - 1)
        return self.get_page()

    def has_next_page(self) -> bool:
        return (self._page + 1) * self.page_size < self.total_count()

    def total_count(self) -> int:
        return len(self._filtered_sorted_rows())

    # === CRUD OPERATIONS ===

    def _generate_new_id(self) -> int:
        if not self._data:
            return 1
        return max(int(r.get("id", 0)) for r in self._data) + 1

    def create_record(self, record: Dict[str, Any]) -> int:
        """Inserts a new record and returns its ID."""
        r = dict(record)
        if "id" not in r:
            r["id"] = self._generate_new_id()
        if "selected" not in r:
            r["selected"] = 0
        self._data.append(r)
        self._columns = list(set(self._columns) | set(r.keys()))
        self._id_index[r["id"]] = len(self._data) - 1
        return r["id"]

    def read_record(self, record_id: Any) -> Optional[Dict[str, Any]]:
        """Reads a single record by its ID."""
        idx = self._id_index.get(record_id)
        if idx is None:
            return None
        return dict(self._data[idx])

    def update_record(self, record_id: Any, updates: Dict[str, Any]) -> bool:
        """Updates a record by ID. Returns True if successful."""
        if not updates:
            return False
        idx = self._id_index.get(record_id)
        if idx is None:
            return False
        self._data[idx].update(updates)
        self._columns = list(set(self._columns) | set(updates.keys()))
        return True

    def delete_record(self, record_id: Any) -> bool:
        """Deletes a record by ID. Returns True if successful."""
        idx = self._id_index.get(record_id)
        if idx is None:
            return False
        self._data.pop(idx)
        # rebuild index (positions changed)
        self._rebuild_id_index()
        return True

    # === SELECTION ====

    def select_record(self, record_id: Any) -> bool:
        """Marks a record as selected (selected = 1)."""
        return self._set_selected_flag(record_id, 1)

    def unselect_record(self, record_id: Any) -> bool:
        """Marks a record as unselected (selected = 0)."""
        return self._set_selected_flag(record_id, 0)

    def select_all(self, current_page_only: bool = False) -> int:
        """Marks all records as selected."""
        self._ensure_selected_column()
        if current_page_only:
            ids = [r["id"] for r in self.get_page()]
            count = 0
            idset = set(ids)
            for r in self._data:
                if r["id"] in idset and r.get("selected") != 1:
                    r["selected"] = 1
                    count += 1
            return count
        else:
            count = 0
            for r in self._data:
                if r.get("selected") != 1:
                    r["selected"] = 1
                    count += 1
            return count

    def unselect_all(self, current_page_only: bool = False) -> int:
        """Unselects all records."""
        self._ensure_selected_column()
        if current_page_only:
            ids = [r["id"] for r in self.get_page()]
            count = 0
            idset = set(ids)
            for r in self._data:
                if r["id"] in idset and r.get("selected") != 0:
                    r["selected"] = 0
                    count += 1
            return count
        else:
            count = 0
            for r in self._data:
                if r.get("selected") != 0:
                    r["selected"] = 0
                    count += 1
            return count

    def _set_selected_flag(self, record_id: Any, flag: int) -> bool:
        self._ensure_selected_column()
        idx = self._id_index.get(record_id)
        if idx is None:
            return False
        self._data[idx]["selected"] = 1 if flag else 0
        return True

    def get_selected(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieves selected records, optionally paginated."""
        self._ensure_selected_column()
        rows = [r for r in self._data if r.get("selected") == 1]
        rows = self._apply_filter_and_sort(rows)  # respect current filter/sort
        if page is None:
            return [dict(r) for r in rows]
        start = max(0, int(page)) * self.page_size
        end = start + self.page_size
        return [dict(r) for r in rows[start:end]]

    def selected_count(self) -> int:
        self._ensure_selected_column()
        return sum(1 for r in self._data if r.get("selected") == 1)

    # === DATA EXPORT ===

    def export_to_csv(self, filepath: str, include_all: bool = True) -> None:
        """Export the data to a CSV file."""
        rows = self._data if include_all else [r for r in self._data if r.get("selected") == 1]
        if not rows:
            return
        # Keep stable set of fieldnames
        fieldnames = list(self._columns) if self._columns else list(rows[0].keys())
        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k) for k in fieldnames})

    # === Misc paging utility ===

    def get_page_from_index(self, start_index: int, count: int) -> List[Dict[str, Any]]:
        rows = self._filtered_sorted_rows()
        start = max(0, int(start_index))
        end = start + max(0, int(count))
        return [dict(r) for r in rows[start:end]]
