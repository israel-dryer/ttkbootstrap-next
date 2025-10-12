from typing import Literal, Optional, Union, Unpack

from ttkbootstrap.core.layout_context import pop_container, push_container
from ttkbootstrap.layouts.base_layout import BaseLayout
from ttkbootstrap.layouts.types import GridOptions
from ttkbootstrap.layouts.utils import add_pad, normalize_gap
from ttkbootstrap.types import Gap, Padding, Sticky


def _parse_size(value: Union[int, str]) -> tuple[int, int]:
    if isinstance(value, int):
        return value, 0
    if isinstance(value, str):
        if value == "auto":
            return 0, 0
        if value.endswith("px"):
            try:
                return 0, int(value[:-2])
            except ValueError:
                return 0, 0
    return 0, 0


class Grid(BaseLayout):
    """Grid container using Tk 'grid' with auto-placement, gap, and padding (guidance-only)."""

    def __init__(
            self,
            *,
            rows: Optional[Union[int, list[Union[int, str]]]] = None,
            columns: Optional[Union[int, list[Union[int, str]]]] = None,
            gap: Gap = 0,
            padding: Padding = 0,
            sticky_items: Optional[Sticky] = None,
            propagate: bool | None = None,
            auto_flow: Literal["row", "column", "dense-row", "dense-column", "none"] = "row",
            **kwargs: Unpack[GridOptions],
    ):
        super().__init__(**kwargs)

        self._gap = self._normalize_gap(gap)
        self._padding = padding
        self._sticky_items = sticky_items
        self._propagate = propagate
        self._auto_flow = auto_flow

        # auto-placement state
        self._next_row = 0
        self._next_col = 0
        self._occupied: set[tuple[int, int]] = set()

        if self._propagate is not None:
            self.widget.grid_propagate(self._propagate)

        # Normalize rows/columns
        if isinstance(rows, int):
            self._rows = [(1, 0)] * rows
        elif isinstance(rows, list) and rows and isinstance(rows[0], (int, str)):
            self._rows = [_parse_size(r) for r in rows]
        else:
            self._rows = []
        if isinstance(columns, int):
            self._columns = [(1, 0)] * columns
        elif isinstance(columns, list) and columns and isinstance(columns[0], (int, str)):
            self._columns = [_parse_size(c) for c in columns]
        else:
            self._columns = []
        for i, (weight, minsize) in enumerate(self._rows):
            self.configure_row(i, weight=weight, minsize=minsize)
        for i, (weight, minsize) in enumerate(self._columns):
            self.configure_column(i, weight=weight, minsize=minsize)

        self.configure(padding=self._padding)

    def __enter__(self):
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        pop_container()

    # --- Guidance only: compute row/col, gaps, sticky, reserve cells -----
    def guide_layout(self, child, method: str, options: dict) -> tuple[str, dict]:
        if method and method != "grid":
            return method, dict(options or {})
        method = "grid"

        opts = dict(options or {})
        row = opts.get("row", getattr(child, "row", None))
        col = opts.get("column", getattr(child, "column", None))
        rowspan = int(opts.get("rowspan", 1) or 1)
        colspan = int(opts.get("columnspan", 1) or 1)
        offset = int(opts.pop("offset", getattr(child, "offset", 0)) or 0)

        # Auto-placement
        if (row is None or col is None) and self._auto_flow != "none":
            placed = False
            cols = len(self._columns) if self._columns else 100
            rows = 100

            def free(r, c) -> bool:
                return all(
                    (r + dr, c + dc) not in self._occupied
                    for dr in range(rowspan) for dc in range(colspan))

            if "dense" in self._auto_flow:
                if self._auto_flow.endswith("row"):
                    for r in range(rows):
                        for c in range(cols):
                            if free(r, c):
                                row, col = r, c;
                                placed = True;
                                break
                        if placed: break
                else:
                    for c in range(cols):
                        for r in range(rows):
                            if free(r, c):
                                row, col = r, c;
                                placed = True;
                                break
                        if placed: break
            else:
                if self._auto_flow.startswith("row"):
                    r, c = self._next_row, self._next_col
                    while not placed:
                        if free(r, c):
                            row, col = r, c;
                            placed = True
                        else:
                            c += 1
                            if self._columns and c >= len(self._columns):
                                c = 0;
                                r += 1
                    self._next_row = r
                    self._next_col = c + colspan
                    if self._columns and self._next_col >= len(self._columns):
                        self._next_col = 0;
                        self._next_row += 1
                else:
                    c, r = self._next_col, self._next_row
                    while not placed:
                        if free(r, c):
                            row, col = r, c;
                            placed = True
                        else:
                            r += 1
                            if r >= rows:
                                r = 0;
                                c += 1
                    self._next_col = c
                    self._next_row = r + rowspan

        col = (col if col is not None else 0) + offset
        row = (row if row is not None else 0)

        # Reserve cells NOW; guidance assumes immediate execution will follow
        for dr in range(rowspan):
            for dc in range(colspan):
                self._occupied.add((row + dr, col + dc))

        guided: dict[str, object] = {"row": row, "column": col}
        col_gap, row_gap = normalize_gap(self._gap)

        # Grid gap on non-first column/row (margins added by child, not here)
        padx = opts.get("padx", None)
        pady = opts.get("pady", None)
        if col > 0 and col_gap:
            padx = add_pad((col_gap, 0), padx)
        if row > 0 and row_gap:
            pady = add_pad((row_gap, 0), pady)
        if padx is not None:
            guided["padx"] = padx
        if pady is not None:
            guided["pady"] = pady

        # Container default sticky
        if self._sticky_items and "sticky" not in opts:
            guided["sticky"] = self._sticky_items

        # Merge so child can still override
        merged = {**guided, **opts}
        return method, merged

    @classmethod
    def _normalize_gap(cls, gap):
        return (gap, gap) if isinstance(gap, int) else gap

    def configure_row(self, index: int, weight: int = 1, minsize: Optional[int] = None):
        self.widget.rowconfigure(index, weight=weight, minsize=minsize or 0)

    def configure_column(self, index: int, weight: int = 1, minsize: Optional[int] = None):
        self.widget.columnconfigure(index, weight=weight, minsize=minsize or 0)

    def default_sticky(self) -> Optional[str]:
        return self._sticky_items

    def preferred_layout_method(self) -> str:
        return "grid"
