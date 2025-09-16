from typing import Any, List, Literal, Optional, Tuple, Union, Unpack, cast

from ttkbootstrap.core.layout_context import pop_container, push_container
from ttkbootstrap.layouts.base_layout import BaseLayout, FrameOptions
from ttkbootstrap.layouts.utils import add_pad, margin_to_pad, normalize_gap
from ttkbootstrap.types import Gap, GridItemOptions, Padding, PlaceItemOptions, Sticky
from ttkbootstrap.utils import assert_valid_keys


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


class GridOptions(FrameOptions, total=False):
    surface: str
    variant: str


class Grid(BaseLayout):
    """Grid container using Tk 'grid' with optional auto-placement, gap, and padding."""

    def __init__(
            self,
            *,
            rows: Optional[Union[int, list[Union[int, str]]]] = None,
            columns: Optional[Union[int, list[Union[int, str]]]] = None,
            gap: Gap = 0,
            padding: Padding = 0,
            sticky_items: Optional[Sticky] = None,
            propagate: bool | None = None,
            auto_flow: Literal['row', 'column', 'dense-row', 'dense-column', 'none'] = 'row',
            **kwargs: Unpack[GridOptions]
    ):
        """Init a grid container.

        Args:
            rows: Row count or spec list (e.g., 1, ["auto", "24px"]).
            columns: Column count or spec list (same as rows).
            gap: Item spacing (int or (x, y)); applied to non-first row/col.
            padding: Inner padding for the container (int or (x, y)).
            sticky_items: Default sticky for children (e.g., "nsew"); None uses Tk default.
            propagate: If False, disable geometry propagation.
            auto_flow: Auto-placement order; 'dense-*' fills gaps; 'none' disables auto-place.
            **kwargs: Extra frame options (e.g., parent, surface, variant, width, height).
        """
        super().__init__(**kwargs)

        self._gap = self._normalize_gap(gap)
        self._padding = padding
        self._sticky_items = sticky_items
        self._propagate = propagate
        self._auto_flow = auto_flow
        self._next_row = 0
        self._next_col = 0
        self._occupied = set()

        # queue + context flag: store (child, method, opts)
        self._layout_children: List[Tuple[Any, str, dict]] = []
        self._in_context: bool = False

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
        """Enter layout context; attach self and push as current container."""
        self._in_context = True
        push_container(self)
        self.attach()
        return self

    def __exit__(self, exc_type, exc, tb):
        """Flush queued children and pop this container from the context."""
        try:
            self._mount_queued_children()
        finally:
            self._in_context = False
            pop_container()

    def register_layout_child(self, child, method: str, opts: dict):
        """Validate and upsert a (child, method, opts) record for 'grid'/'place';
        queues only—mounts on context exit/flush."""
        if method not in ("grid", "place"):
            return
        if method == "grid":
            assert_valid_keys(opts, GridItemOptions, where="grid")
        else:
            assert_valid_keys(opts, PlaceItemOptions, where="place")
        for i, (c, m, _) in enumerate(self._layout_children):
            if c is child:
                self._layout_children[i] = (child, method, dict(opts))
                break
        else:
            self._layout_children.append((child, method, dict(opts)))

    def add(self, child, **grid_options: Unpack[GridItemOptions]):
        """Queue or update a child with grid options.
        Mounts on context exit or explicit flush.
        """
        assert_valid_keys(grid_options, GridItemOptions, where="grid")
        if not grid_options and hasattr(child, "_saved_layout") and (saved_layout := getattr(child, "_saved_layout")):
            m, saved = saved_layout
            if m == "grid":
                grid_options = dict(saved)
        # upsert
        for i, (c, m, _) in enumerate(self._layout_children):
            if c is child and m == "grid":
                self._layout_children[i] = (child, "grid", grid_options)
                break
        else:
            self._layout_children.append((child, "grid", grid_options))
        if not self._in_context:
            self._mount_queued_children()

    # drain queue
    def _mount_queued_children(self):
        while self._layout_children:
            child, method, opts = self._layout_children.pop(0)
            if method == "grid":
                self._mount_child_grid(child, **opts)
            elif method == "place":
                self._mount_child_place(child, opts)

    # realization
    def _mount_child_grid(self, child, **options: Unpack[GridItemOptions]):
        grid_options = dict(**options)
        widget = getattr(child, "widget", child)
        row = grid_options.get("row", getattr(child, "row", None))
        col = grid_options.get("column", getattr(child, "column", None))
        rowspan = grid_options.get("rowspan", 1)
        colspan = grid_options.get("columnspan", 1)
        offset = grid_options.pop("offset", getattr(child, "offset", 0)) or 0

        # Auto-placement logic (unchanged)
        if row is None or col is None:
            placed = False
            cols = len(self._columns) if self._columns else 100
            rows = 100
            if 'dense' in self._auto_flow:
                if self._auto_flow.endswith('row'):
                    for r in range(rows):
                        for c in range(cols):
                            if all(
                                    (r + dr, c + dc) not in self._occupied
                                    for dr in range(rowspan) for dc in range(colspan)):
                                row, col = r, c
                                placed = True
                                break
                        if placed: break
                else:
                    for c in range(cols):
                        for r in range(rows):
                            if all(
                                    (r + dr, c + dc) not in self._occupied
                                    for dr in range(rowspan) for dc in range(colspan)):
                                row, col = r, c
                                placed = True
                                break
                        if placed: break
            else:
                if self._auto_flow.startswith('row'):
                    r, c = self._next_row, self._next_col
                    while not placed:
                        if all(
                                (r + dr, c + dc) not in self._occupied
                                for dr in range(rowspan) for dc in range(colspan)):
                            row, col = r, c
                            placed = True
                        else:
                            c += 1
                            if self._columns and c >= len(self._columns):
                                c = 0
                                r += 1
                    self._next_row = r
                    self._next_col = c + colspan
                    if self._columns and self._next_col >= len(self._columns):
                        self._next_col = 0
                        self._next_row += 1
                elif self._auto_flow.startswith('column'):
                    c, r = self._next_col, self._next_row
                    while not placed:
                        if all(
                                (r + dr, c + dc) not in self._occupied
                                for dr in range(rowspan) for dc in range(colspan)):
                            row, col = r, c
                            placed = True
                        else:
                            r += 1
                            if r >= rows:
                                r = 0
                                c += 1
                    self._next_col = c
                    self._next_row = r + rowspan

        col = (col if col is not None else 0) + offset

        for dr in range(rowspan):
            for dc in range(colspan):
                self._occupied.add((row + dr, col + dc))

        grid_options["row"] = row
        grid_options["column"] = col

        col_gap, row_gap = normalize_gap(self._gap)

        margin_x, margin_y = (0, 0)
        if hasattr(child, "margin"):
            margin_x, margin_y = margin_to_pad(child.margin)

        padx = grid_options.get("padx", None)
        pady = grid_options.get("pady", None)

        if col > 0:
            padx = add_pad((col_gap, 0), padx or margin_x)
        else:
            padx = padx or margin_x

        if row > 0:
            pady = add_pad((row_gap, 0), pady or margin_y)
        else:
            pady = pady or margin_y

        if padx: grid_options["padx"] = padx
        if pady: grid_options["pady"] = pady

        if self._sticky_items and "sticky" not in grid_options:
            grid_options["sticky"] = cast(Sticky, self._sticky_items)

        widget.grid(**grid_options)

    @classmethod
    def _normalize_gap(cls, gap):
        return (gap, gap) if isinstance(gap, int) else gap

    def configure_row(self, index: int, weight: int = 1, minsize: Optional[int] = None):
        """Set a grid row's expand weight and minimum height (px)."""
        self.widget.rowconfigure(index, weight=weight, minsize=minsize or 0)

    def configure_column(self, index: int, weight: int = 1, minsize: Optional[int] = None):
        """Set a grid column's expand weight and minimum width (px)."""
        self.widget.columnconfigure(index, weight=weight, minsize=minsize or 0)

    def default_sticky(self) -> Optional[str]:
        """Return the default sticky (e.g., 'nsew') for child grid items."""
        return self._sticky_items

    def preferred_layout_method(self) -> str:
        """Return the container’s preferred layout method ('grid')."""
        return "grid"
