"""
FlexGrid: a grid-first container with smart gaps, simple auto-placement,
and a unified expand API.

Strategy
--------
- **No spacer tracks.** Visual gaps are created with per-cell padding
  (`padx/pady`) split between neighbors; the outermost edges are trimmed
  so the last column/row has no gap on its right/bottom.
- **Auto-placement.** Children flow left-to-right across `columns`, wrap
  to the next row automatically, and keep their declared `row/col` if
  provided. When the layout wraps to a new row, the old last row is
  converted to an interior row and its bottom gap is backfilled.
- **Unified expand.** `expand` sets uniform weights for *this container’s*
  grid tracks (columns/rows). It does not touch the parent; the parent
  must still give the FlexGrid’s cell room to grow (e.g., `parent.rowconfigure`).
- **Sticky by default.** You can set a container-wide `sticky_items` to
  apply to children that don’t specify their own `sticky`.
- **Track modeling.** `columns`/`rows` accept integer weights or fixed
  pixel tracks via `"Npx"`. Integers configure `grid_*configure(..., weight=N)`;
  the expand override (if set) wins uniformly.

Typical gotcha
--------------
`expand` affects *tracks*, not widgets. A child fills its cell only if
its own `sticky` allows it (e.g., `"nsew"`), and the *parent* grid gives
the FlexGrid room (non-zero row/column weights).
"""

from __future__ import annotations
from typing import Any, Unpack, Union, TypedDict, Optional

from ttkbootstrap.core.base_widget_alt import BaseWidget
from ttkbootstrap.layouts.frame import Frame
from ttkbootstrap.layouts.constants import layout_context_stack
from ttkbootstrap.layouts.types import Sticky, SemanticLayoutOptions
from ttkbootstrap.layouts.utils import add_pad, margin_to_pad, normalize_gap, normalize_padding
from ttkbootstrap.style.tokens import SurfaceColor
from ttkbootstrap.widgets.types import FrameOptions


class GridLayoutOptions(FrameOptions, total=False):
    """Per-child grid options consumed by FlexGrid."""
    row: int
    col: int
    rowspan: int
    colspan: int
    offset: int
    sticky: Sticky
    padx: int | tuple[int, int]
    pady: int | tuple[int, int]


class GridRowOptions(TypedDict, total=False):
    """Row configuration passed to `rowconfigure`."""
    weight: int
    height: int


class GridColumnOptions(TypedDict, total=False):
    """Column configuration passed to `columnconfigure`."""
    weight: int
    width: int


class _Options(GridLayoutOptions, SemanticLayoutOptions, total=False):
    """Extra container styling options forwarded to Frame."""
    surface: SurfaceColor
    variant: str


class FlexGrid(Frame):
    """
    Flexbox-inspired grid layout with smart gaps, auto-placement,
    and flexible track growth rules.

    Growth rules:
    -------------
    1. **Both `columns` and `rows` explicitly set** → Columns are fixed.
       Additional rows are appended as needed when items wrap.
    2. **Neither `columns` nor `rows` set** → Defaults to 1 column.
       Rows are appended as needed (vertical stacking).
    3. **`rows == 1` and `columns` not set** → Stays in a single row.
       Columns are appended as needed (horizontal growth).
    4. **`rows > 1` and any `columns` value** → Rows are appended as needed.

    Features:
    ---------
    - **No spacer tracks:** Visual gaps are implemented with per-cell
      `padx/pady` split between neighbors; outer edges are trimmed so the
      last column/row has no trailing gap.
    - **Auto-placement:** Items flow left-to-right across available columns
      and wrap to a new row (or grow columns, per rules).
    - **Unified expand:** The `expand` argument sets uniform track weights
      for this container’s grid tracks; the parent must still allow the
      container to grow.
    - **Default stickiness:** `sticky_items` applies to children without
      an explicit `sticky`.

    Args:
        parent: Parent widget/container.
        gap: Gap between cells as `(col_gap, row_gap)` or single int.
        padding: Inner padding for the FlexGrid container.
        columns: Int (count of equal-weight columns) or list of track specs
                 (`int` weight or `"Npx"` fixed track).
        rows: Optional int or list of track specs. Behavior changes per rules above.
        propagate: Whether Tk’s grid propagation is enabled for this container.
        sticky_items: Default sticky applied to children.
        expand: Sets uniform column/row weights for this container’s tracks.
        **kwargs: Forwarded to `Frame`.
    """

    _Default = object()  # sentinel to detect "not provided"

    def __init__(
            self,
            parent=None,
            *,
            gap: int | tuple[int, int] = 0,
            padding: Union[int, tuple[int, int], tuple[int, int, int, int]] = 0,
            columns: int | list[str | int] | None | Any = _Default,
            rows: int | list[str | int] | None = None,
            propagate: bool = True,
            sticky_items: Sticky | None = None,
            expand: bool | int | tuple[int | bool, int | bool] | None = None,
            **kwargs: Unpack[_Options]
    ):
        self._gap = normalize_gap(gap)
        self._padding = normalize_padding(padding)

        # Were args explicitly provided?
        cols_provided = (columns is not self._Default)
        rows_provided = (rows is not None)

        # Normalize initial columns list
        if not cols_provided:
            # columns not provided
            init_columns: list[str | int] = []  # may grow later based on rules
        elif columns is None:
            init_columns = []
        elif isinstance(columns, list):
            init_columns = list(columns)
        else:
            # int count → equal-weight tracks
            init_columns = [1] * int(columns)

        # Normalize initial rows list
        if rows is None:
            init_rows: list[str | int] = []
        elif isinstance(rows, list):
            init_rows = list(rows)
        else:
            # int count → equal-weight tracks
            init_rows = [1] * int(rows)

        # Determine growth mode per rules
        # - Default behavior is to grow rows as needed.
        # - Special case: if rows == 1 and columns not provided → grow columns only.
        self._grow_columns_only = (not cols_provided) and (len(init_rows) == 1)

        # If neither provided → default to 1 column, grow rows as needed.
        if (not cols_provided) and (not rows_provided) and not self._grow_columns_only:
            init_columns = [1]  # rule #2

        # Stash tracks
        self._columns: list[str | int] = init_columns
        self._rows: list[str | int] = init_rows

        self._auto_layout = True
        self._next_row = 0
        self._next_col = 0
        self._mounted: dict[BaseWidget, dict] = {}

        self._sticky_items = sticky_items
        self._col_weight_default, self._row_weight_default = self._parse_expand(expand)

        super().__init__(parent, padding=self._padding, **kwargs)
        self.widget.grid_propagate(propagate)

        # Configure any predeclared columns
        for index, col in enumerate(self._columns):
            self._configure_column_from_spec(index, col)

        # Configure any predeclared rows
        for index, row in enumerate(self._rows):
            self._configure_row_from_spec(index, row)

        # Ensure at least one column exists in row-growing modes
        if not self._grow_columns_only and not self._columns:
            self._ensure_columns(1)

    # -- context manager (unchanged) ------------------------------------

    def __enter__(self):
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        layout_context_stack().pop()

    # -- public API (unchanged signatures) -------------------------------

    def add(self, widget: BaseWidget):
        layout_options = getattr(widget, "_layout_options", {}).copy()
        if not (layout_options.get("sticky") or "").strip():
            if self._sticky_items:
                layout_options["sticky"] = self._sticky_items
        widget._layout_options = layout_options
        self._add(widget, **layout_options)

    def add_all(self, widgets: list[BaseWidget | tuple[BaseWidget, GridLayoutOptions]]):
        for item in widgets:
            if isinstance(item, tuple):
                widget, opts = item
                self._add(widget, **opts)
            else:
                self.add(item)

    def remove(self, widget: BaseWidget):
        if widget in self._mounted:
            widget.widget.grid_forget()
            del self._mounted[widget]

    def configure_row(self, index: int, **options: Unpack[GridRowOptions]):
        self.widget.rowconfigure(index, **options)

    def configure_column(self, index: int, **options: Unpack[GridColumnOptions]):
        self.widget.columnconfigure(index, **options)

    def configure_child(self, widget: BaseWidget, option: str = None, **options: Unpack[GridLayoutOptions]):
        if widget not in self._mounted:
            raise ValueError("Widget is not managed by this layout.")
        if option:
            return self._mounted[widget].get(option)
        else:
            self.remove(widget)
            self._add(widget, **options)
            return self

    # -- internals -------------------------------------------------------

    def _configure_column_from_spec(self, index: int, spec: str | int):
        if isinstance(spec, int):
            weight = spec
        elif isinstance(spec, str) and spec.endswith("px"):
            weight = 0
            self.widget.grid_columnconfigure(index, minsize=int(spec.removesuffix("px")))
        else:
            weight = 0
        if self._col_weight_default is not None:
            weight = self._col_weight_default
        self.configure_column(index, weight=weight)

    def _configure_row_from_spec(self, index: int, spec: str | int):
        if isinstance(spec, int):
            weight = spec
        elif isinstance(spec, str) and spec.endswith("px"):
            weight = 0
            self.widget.grid_rowconfigure(index, minsize=int(spec.removesuffix("px")))
        else:
            weight = 0
        if self._row_weight_default is not None:
            weight = self._row_weight_default
        self.configure_row(index, weight=weight)

    def _ensure_columns(self, total_needed: int):
        """Append columns up to `total_needed` and configure them."""
        while len(self._columns) < total_needed:
            # Choose a sensible default for new columns
            base = self._columns[0] if self._columns else 1
            self._columns.append(base if isinstance(base, int) else 1)
            idx = len(self._columns) - 1
            self._configure_column_from_spec(idx, self._columns[idx])

    def _ensure_rows(self, total_needed: int):
        """Append rows up to `total_needed` and configure them."""
        while len(self._rows) < total_needed:
            base = self._rows[0] if self._rows else 0
            self._rows.append(base if isinstance(base, int) else 0)
            idx = len(self._rows) - 1
            self._configure_row_from_spec(idx, self._rows[idx])

    def _apply_auto_layout(self, options: GridLayoutOptions) -> GridLayoutOptions:
        """Compute next (row, col) based on flow and handle growth rules."""
        col_span = options.get("colspan", 1)
        offset = options.pop("offset", 0)

        if self._grow_columns_only:
            # Stay on row 0, extend columns as needed, never wrap to a new row.
            needed_cols = self._next_col + offset + col_span
            self._ensure_columns(needed_cols)

            options.setdefault("row", 0)
            options.setdefault("col", self._next_col + offset)
            self._next_col += offset + col_span

            # Ensure weights for any new spans
            if self._col_weight_default is not None:
                for c in range(options["col"], options["col"] + col_span):
                    self.configure_column(c, weight=self._col_weight_default)

            # Row weights: just row 0
            if self._row_weight_default is not None:
                self.configure_row(0, weight=self._row_weight_default)

            return options

        # Grow rows as needed (default & all other rules)
        cols = max(1, len(self._columns))
        will_wrap = (self._next_col + offset + col_span) > cols
        if will_wrap:
            # Old last row becomes interior → give it bottom gap
            self._make_prev_last_row_interior(self._next_row)
            self._next_row += 1
            self._next_col = 0

        # If wrapping created a new row beyond any explicit rows, append it.
        self._ensure_rows(self._next_row + 1)

        options.setdefault("row", self._next_row)
        options.setdefault("col", self._next_col + offset)
        self._next_col += offset + col_span

        # Ensure weights for spans/new tracks
        if self._col_weight_default is not None:
            for c in range(options["col"], options["col"] + col_span):
                self.configure_column(c, weight=self._col_weight_default)
        if self._row_weight_default is not None:
            for r in range(options["row"], options["row"] + options.get("rowspan", 1)):
                self.configure_row(r, weight=self._row_weight_default)

        return options

    def _add(self, widget: BaseWidget, **options: Unpack[GridLayoutOptions]):
        if self._auto_layout:
            options = self._apply_auto_layout(options)

        col = options.get("col", 0)
        row = options.get("row", 0)
        col_span = options.get("colspan", 1)
        row_span = options.get("rowspan", 1)
        sticky = options.get("sticky", "")

        gap_x, gap_y = self._gap

        # Base gap pads centered between cells
        left_pad = gap_x // 2
        right_pad = gap_x - left_pad
        top_pad = gap_y // 2
        bot_pad = gap_y - top_pad

        # Trim outer COL edges
        if col == 0:
            left_pad = 0
        if (col + col_span) == len(self._columns):
            right_pad = 0

        # Trim outer ROW edges
        if self._grow_columns_only:
            # Single row layout → always suppress bottom gap
            bot_pad = 0
            top_pad = 0 if row == 0 else top_pad
        elif self._rows:
            if (row + row_span) >= len(self._rows):
                bot_pad = 0
        else:
            if row == self._next_row:
                bot_pad = 0

        pad_x = (left_pad, right_pad)
        pad_y = (top_pad if row != 0 else 0, bot_pad)

        # Merge margin and explicit padx/pady
        margin = options.pop("margin", 0)
        m_padx, m_pady = margin_to_pad(margin)
        pad_x = add_pad(pad_x, m_padx)
        pad_y = add_pad(pad_y, m_pady)
        if "padx" in options:
            pad_x = add_pad(pad_x, options["padx"])
        if "pady" in options:
            pad_y = add_pad(pad_y, options["pady"])

        # Ensure expand defaults apply to spans/new tracks
        if self._col_weight_default is not None:
            for c in range(col, col + col_span):
                self.configure_column(c, weight=self._col_weight_default)
        if self._row_weight_default is not None:
            for r in range(row, row + row_span):
                self.configure_row(r, weight=self._row_weight_default)

        widget.grid(
            row=row,
            column=col,
            rowspan=row_span,
            columnspan=col_span,
            sticky=sticky,
            padx=pad_x,
            pady=pad_y,
        )

        self._mounted[widget] = dict(
            row=row, col=col,
            row_span=row_span, col_span=col_span,
            sticky=sticky, pad_x=pad_x, pad_y=pad_y,
        )

    def _make_prev_last_row_interior(self, prev_last_row: int):
        gap_y = self._gap[1]
        if gap_y == 0 or not self._mounted:
            return
        interior_bottom = gap_y - (gap_y // 2) if prev_last_row > 0 else gap_y
        for w, info in list(self._mounted.items()):
            if info["row"] == prev_last_row:
                top, current_bottom = info["pad_y"]
                new_bottom = current_bottom + interior_bottom
                w.widget.grid_configure(pady=(top, new_bottom))
                info["pad_y"] = (top, new_bottom)

    @staticmethod
    def _parse_expand(value: bool | int | tuple[int | bool, int | bool] | None) -> tuple[Optional[int], Optional[int]]:
        if value is None:
            return None, None
        if isinstance(value, bool):
            w = 1 if value else 0
            return w, w
        if isinstance(value, int):
            w = max(0, value)
            return w, w
        if isinstance(value, tuple) and len(value) == 2:
            def as_int(x): return 1 if x is True else (0 if x is False else max(0, int(x)))

            return as_int(value[0]), as_int(value[1])
        return None, None
