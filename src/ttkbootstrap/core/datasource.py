import csv
import sqlite3
from typing import Any, Dict, List, Optional


class DataSource:
    """
    In-memory SQLite-backed data manager with pagination, sorting, filtering,
    inferred schema, and full CRUD support.
    """

    def __init__(self, page_size: int = 10):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.page_size = page_size
        self._table = "records"
        self._where = ""
        self._order_by = ""
        self._page = 0
        self._columns = []

    @classmethod
    def _infer_type(cls, value: Any) -> str:
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, bytes):
            return "BLOB"
        return "TEXT"

    def set_data(self, records: List[Dict[str, Any]]):
        if not records:
            return

        # Ensure each record has an 'id'
        for i, record in enumerate(records):
            if "id" not in record:
                record["id"] = i

            if "selected" not in record:
                record["selected"] = 0

        self._columns = list(records[0].keys())
        col_types = {col: self._infer_type(records[0][col]) for col in self._columns}
        col_definitions = ", ".join(
            f"{col} {col_types[col]}" + (" PRIMARY KEY" if col == "id" else "")
            for col in self._columns
        )

        self.conn.execute(f"DROP TABLE IF EXISTS {self._table}")
        self.conn.execute(f"CREATE TABLE {self._table} ({col_definitions})")

        with self.conn:
            for row in records:
                placeholders = ", ".join("?" for _ in self._columns)
                values = tuple(row.get(col) for col in self._columns)
                self.conn.execute(f"INSERT INTO {self._table} VALUES ({placeholders})", values)

    def set_filter(self, where_sql: str = ""):
        self._where = where_sql

    def set_sort(self, order_by_sql: str = ""):
        self._order_by = order_by_sql

    def get_page(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        if page is not None:
            self._page = page
        offset = self._page * self.page_size

        query = f"SELECT * FROM {self._table}"
        if self._where:
            query += f" WHERE {self._where}"
        if self._order_by:
            query += f" ORDER BY {self._order_by}"
        query += f" LIMIT {self.page_size} OFFSET {offset}"

        cursor = self.conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def next_page(self) -> List[Dict[str, Any]]:
        self._page += 1
        return self.get_page()

    def prev_page(self) -> List[Dict[str, Any]]:
        self._page = max(0, self._page - 1)
        return self.get_page()

    def has_next_page(self) -> bool:
        return (self._page + 1) * self.page_size < self.total_count()

    def total_count(self) -> int:
        query = f"SELECT COUNT(*) FROM {self._table}"
        if self._where:
            query += f" WHERE {self._where}"
        return self.conn.execute(query).fetchone()[0]

    # === CRUD OPERATIONS ===

    def create_record(self, record: Dict[str, Any]) -> int:
        """Inserts a new record and returns its ID."""
        if "id" not in record:
            record["id"] = self._generate_new_id()

        if "selected" not in record:
            record["selected"] = 0

        keys = record.keys()
        cols = ", ".join(keys)
        placeholders = ", ".join("?" for _ in keys)
        values = tuple(record[col] for col in keys)

        with self.conn:
            self.conn.execute(f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})", values)
        return record["id"]

    def read_record(self, record_id: Any) -> Optional[Dict[str, Any]]:
        """Reads a single record by its ID."""
        cursor = self.conn.execute(f"SELECT * FROM {self._table} WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_record(self, record_id: Any, updates: Dict[str, Any]) -> bool:
        """Updates a record by ID. Returns True if successful."""
        if not updates:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = tuple(updates.values()) + (record_id,)
        with self.conn:
            cur = self.conn.execute(f"UPDATE {self._table} SET {set_clause} WHERE id = ?", values)
            return cur.rowcount > 0

    def delete_record(self, record_id: Any) -> bool:
        """Deletes a record by ID. Returns True if successful."""
        with self.conn:
            cur = self.conn.execute(f"DELETE FROM {self._table} WHERE id = ?", (record_id,))
            return cur.rowcount > 0

    def _generate_new_id(self) -> int:
        """Finds the next available integer ID."""
        cursor = self.conn.execute(f"SELECT MAX(id) FROM {self._table}")
        max_id = cursor.fetchone()[0]
        return (max_id or 0) + 1

    # === SELECTION ====

    def select_record(self, record_id: Any) -> bool:
        """
        Marks a record as selected by setting `selected = 1`.

        Args:
            record_id: The unique ID of the record to select.

        Returns:
            True if the record was updated, False otherwise.
        """
        return self._set_selected_flag(record_id, 1)

    def unselect_record(self, record_id: Any) -> bool:
        """
        Marks a record as unselected by setting `selected = 0`.

        Args:
            record_id: The unique ID of the record to unselect.

        Returns:
            True if the record was updated, False otherwise.
        """
        return self._set_selected_flag(record_id, 0)

    def select_all(self, current_page_only: bool = False) -> int:
        """
        Marks all records as selected.

        Args:
            current_page_only: If True, selects only the current page.

        Returns:
            The number of rows updated.
        """
        self._ensure_selected_column()
        if current_page_only:
            ids = [row["id"] for row in self.get_page()]
            if not ids:
                return 0
            placeholders = ", ".join("?" for _ in ids)
            query = f"UPDATE {self._table} SET selected = 1 WHERE id IN ({placeholders})"
            with self.conn:
                cur = self.conn.execute(query, ids)
                return cur.rowcount
        else:
            with self.conn:
                cur = self.conn.execute(f"UPDATE {self._table} SET selected = 1")
                return cur.rowcount

    def unselect_all(self, current_page_only: bool = False) -> int:
        """
        Unselects all records.

        Args:
            current_page_only: If True, unselects only the current page.

        Returns:
            The number of rows updated.
        """
        self._ensure_selected_column()
        if current_page_only:
            ids = [row["id"] for row in self.get_page()]
            if not ids:
                return 0
            placeholders = ", ".join("?" for _ in ids)
            query = f"UPDATE {self._table} SET selected = 0 WHERE id IN ({placeholders})"
            with self.conn:
                cur = self.conn.execute(query, ids)
                return cur.rowcount
        else:
            with self.conn:
                cur = self.conn.execute(f"UPDATE {self._table} SET selected = 0")
                return cur.rowcount

    def get_selected(self, page: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieves selected records, optionally paginated.

        Args:
            page: Optional page number. If None, return all selected records.

        Returns:
            A list of selected row dictionaries.
        """
        self._ensure_selected_column()
        query = f"SELECT * FROM {self._table} WHERE selected = 1"

        if page is not None:
            offset = page * self.page_size
            query += f" LIMIT {self.page_size} OFFSET {offset}"

        cursor = self.conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def _ensure_selected_column(self):
        """
        Adds the `selected` column to the table if it does not exist.
        """
        if "selected" not in self._columns:
            with self.conn:
                self.conn.execute(f"ALTER TABLE {self._table} ADD COLUMN selected INTEGER DEFAULT 0")
            self._columns.append("selected")

    def selected_count(self) -> int:
        """
        Returns the total number of selected records.
        """
        self._ensure_selected_column()
        query = f"SELECT COUNT(*) FROM {self._table} WHERE selected = 1"
        return self.conn.execute(query).fetchone()[0]

    def _set_selected_flag(self, record_id: Any, flag: int) -> bool:
        """
        Internal method to update the `selected` field for a record.

        Args:
            record_id: The ID of the record to update.
            flag: 1 for selected, 0 for unselected.

        Returns:
            True if update was successful.
        """
        if "selected" not in self._columns:
            # Add selected column if it doesn't exist
            with self.conn:
                self.conn.execute(f"ALTER TABLE {self._table} ADD COLUMN selected INTEGER DEFAULT 0")
            self._columns.append("selected")

        with self.conn:
            cur = self.conn.execute(f"UPDATE {self._table} SET selected = ? WHERE id = ?", (flag, record_id))
            return cur.rowcount > 0

    # === DATA EXPORT ===

    def export_to_csv(self, filepath: str, include_all: bool = True):
        """
        Export the data to a CSV file.

        Args:
            filepath: Path to the output CSV file.
            include_all: If True, exports all records.
                         If False, exports only selected records.
        """
        self._ensure_selected_column()
        query = f"SELECT * FROM {self._table}"
        if not include_all:
            query += " WHERE selected = 1"

        cursor = self.conn.execute(query)
        rows = cursor.fetchall()

        if not rows:
            return

        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))
