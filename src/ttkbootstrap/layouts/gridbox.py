"""
GridBox: a grid-first container with smart gaps, simple auto-placement,
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
  must still give the GridBox’s cell room to grow (e.g., `parent.rowconfigure`).
- **Sticky by default.** You can set a container-wide `sticky_items` to
  apply to children that don’t specify their own `sticky`.
- **Track modeling.** `columns`/`rows` accept integer weights or fixed
  pixel tracks via `"Npx"`. Integers configure `grid_*configure(..., weight=N)`;
  the expand override (if set) wins uniformly.

Typical gotcha
--------------
`expand` affects *tracks*, not widgets. A child fills its cell only if
its own `sticky` allows it (e.g., `"nsew"`), and the *parent* grid gives
the GridBox room (non-zero row/column weights).
"""

from __future__ import annotations
from typing import Unpack, Union, TypedDict, Optional

from ttkbootstrap.core.base_widget_alt import BaseWidget
from ttkbootstrap.layouts.frame import Frame
from ttkbootstrap.layouts.constants import layout_context_stack
from ttkbootstrap.layouts.types import Sticky, SemanticLayoutOptions
from ttkbootstrap.layouts.utils import add_pad, margin_to_pad, normalize_gap, normalize_padding
from ttkbootstrap.style.tokens import SurfaceColor
from ttkbootstrap.widgets.types import FrameOptions


class GridLayoutOptions(FrameOptions, total=False):
    """Per-child grid options consumed by GridBox."""
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


class GridBox(Frame):
    """
    Grid-first layout with smart gaps, simple auto-placement, and a unified
    `expand` parameter for track weights.

    __init__(...) doc
    ------------------
    Args:
        parent: The parent widget/container.
        gap: Gap between cells as `(col_gap, row_gap)` or a single int. Implemented
            via per-cell `padx/pady` split between neighbors. The first column/row
            omits its left/top share; the last column/row omits its right/bottom
            share so there’s no trailing gap.
        padding: Inner padding for the GridBox itself. Accepts `int`, `(x, y)`,
            or `(left, top, right, bottom)`.
        columns: Either an integer (count of equal-weight columns) or a list of
            track specs (`int` weight or `"Npx"` fixed track). Default `1` so
            stacked layouts “just work” without extra args.
        rows: Optional list of row track specs (`int` weight or `"Npx"`). If not
            provided, rows are created on demand by auto-placement.
        propagate: Passed to Tk grid propagation for this container.
        sticky_items: Default `sticky` applied to children that do not specify
            `sticky` themselves (e.g., `"nsew"`).
        expand: Unified expand shortcut for *this container’s* tracks:
            - `True` / `1`        → columns and rows weight = 1
            - `(c, r)`            → columns weight = `c`, rows weight = `r`
                                     (bools map to 1/0)
            - `None` (default)    → leave weights as declared by `columns` / `rows`
            This does not configure the **parent** grid. If you grid the GridBox
            into a parent, ensure the parent gives its cell room to grow
            (e.g., `parent.rowconfigure(0, weight=1)` and `parent.columnconfigure(0, weight=1)`).
        **kwargs: Forwarded to `Frame` (e.g., `surface`, `style`, etc.).

    Notes:
        - `expand` applies uniformly to **all** tracks in this container (and to
          on-demand tracks created by auto-placement). For per-track variation,
          keep `expand=None` and specify explicit `columns=[...]` and/or `rows=[...]`.
        - Children still need an appropriate `sticky` to fill their own cells.
    """

    def __init__(
            self,
            parent=None,
            *,
            gap: int | tuple[int, int] = 0,
            padding: Union[int, tuple[int, int], tuple[int, int, int, int]] = 0,
            columns: int | list[str | int] = 1,
            rows: int | list[str | int] | None = None,
            propagate: bool = True,
            sticky_items: Sticky | None = None,
            expand: bool | int | tuple[int | bool, int | bool] | None = None,
            **kwargs: Unpack[_Options]
    ):
        self._gap = normalize_gap(gap)
        self._padding = normalize_padding(padding)
        self._columns = columns if isinstance(columns, list) else [1] * columns
        self._rows = rows if isinstance(rows, list) else []
        self._auto_layout = True
        self._next_row = 0
        self._next_col = 0
        self._mounted: dict[BaseWidget, dict] = {}

        self._sticky_items = sticky_items
        self._col_weight_default, self._row_weight_default = self._parse_expand(expand)

        super().__init__(parent, padding=self._padding, **kwargs)
        self.widget.grid_propagate(propagate)

        # Configure columns
        for index, col in enumerate(self._columns):
            if isinstance(col, int):
                weight = col
            elif isinstance(col, str) and col.endswith("px"):
                weight = 0
                self.widget.grid_columnconfigure(index, minsize=int(col.removesuffix("px")))
            else:
                weight = 0
            if self._col_weight_default is not None:
                weight = self._col_weight_default
            self.configure_column(index, weight=weight)

        # Configure rows (if declared up front)
        if self._rows:
            for index, row in enumerate(self._rows):
                if isinstance(row, int):
                    weight = row
                elif isinstance(row, str) and row.endswith("px"):
                    weight = 0
                    self.widget.grid_rowconfigure(index, minsize=int(row.removesuffix("px")))
                else:
                    weight = 0
                if self._row_weight_default is not None:
                    weight = self._row_weight_default
                self.configure_row(index, weight=weight)

    # -- context manager -------------------------------------------------

    def __enter__(self):
        """Enter a layout context where child widgets auto-mount into this container."""
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        """Exit the layout context."""
        layout_context_stack().pop()

    # -- public API ------------------------------------------------------

    def add(self, widget: BaseWidget):
        """Add and grid a child with auto-placement and smart gaps."""
        layout_options = getattr(widget, "_layout_options", {}).copy()

        # Default sticky for items, if caller didn't set one
        if not (layout_options.get("sticky") or "").strip():
            if self._sticky_items:
                layout_options["sticky"] = self._sticky_items

        widget._layout_options = layout_options
        self._add(widget, **layout_options)

    def add_all(self, widgets: list[BaseWidget | tuple[BaseWidget, GridLayoutOptions]]):
        """Add multiple children; tuples may include explicit per-child grid options."""
        for item in widgets:
            if isinstance(item, tuple):
                widget, opts = item
                self._add(widget, **opts)
            else:
                self.add(item)

    def remove(self, widget: BaseWidget):
        """Remove a managed child from the grid."""
        if widget in self._mounted:
            widget.widget.grid_forget()
            del self._mounted[widget]

    def configure_row(self, index: int, **options: Unpack[GridRowOptions]):
        """Forward to `rowconfigure`."""
        self.widget.rowconfigure(index, **options)

    def configure_column(self, index: int, **options: Unpack[GridColumnOptions]):
        """Forward to `columnconfigure`."""
        self.widget.columnconfigure(index, **options)

    def configure_child(
            self,
            widget: BaseWidget,
            option: str = None,
            **options: Unpack[GridLayoutOptions]
    ):
        """
        Re-grid a managed child with new options, or read a stored option.

        Args:
            widget: The child to reconfigure.
            option: If provided, returns the stored value for this key instead of
                reconfiguring the child.
            **options: New grid options to apply.
        """
        if widget not in self._mounted:
            raise ValueError("Widget is not managed by this layout.")
        if option:
            return self._mounted[widget].get(option)
        else:
            self.remove(widget)
            self._add(widget, **options)
            return self

    # -- internals -------------------------------------------------------

    def _apply_auto_layout(self, options: GridLayoutOptions) -> GridLayoutOptions:
        """Compute next (row, col) based on flow and handle row wraps."""
        col_span = options.get("colspan", 1)
        offset = options.pop("offset", 0)
        cols = len(self._columns)

        # Will this placement wrap to a NEW ROW?
        will_wrap = (self._next_col + offset + col_span) > cols
        if will_wrap:
            # Old "last row" becomes interior → give it bottom gap
            self._make_prev_last_row_interior(self._next_row)
            self._next_row += 1
            self._next_col = 0

        options.setdefault("row", self._next_row)
        options.setdefault("col", self._next_col + offset)
        self._next_col += offset + col_span

        # If expand specified for rows, ensure new rows inherit that weight
        if self._row_weight_default is not None:
            self.configure_row(options["row"], weight=self._row_weight_default)

        return options

    def _add(self, widget: BaseWidget, **options: Unpack[GridLayoutOptions]):
        """Grid the child with computed gaps, margins, and expand semantics."""
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
        if (col + col_span) == len(self._columns):  # rightmost edge
            right_pad = 0

        # Trim outer ROW edges
        if self._rows:
            # If explicitly-declared rows exist, suppress bottom gap for the last one.
            if (row + row_span) >= len(self._rows):
                bot_pad = 0
        else:
            # In auto-layout mode, the current "last row" is `_next_row`.
            # Any item in that row should suppress bottom gap (we backfill later on wrap).
            if row == self._next_row:
                bot_pad = 0

        pad_x = (left_pad, right_pad)
        pad_y = (top_pad if row != 0 else 0, bot_pad)  # first row gets no top gap

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
        """When a new row is created, the old last row becomes interior; add its bottom gap."""
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

    # -- helpers ---------------------------------------------------------

    @staticmethod
    def _parse_expand(value: bool | int | tuple[int | bool, int | bool] | None) -> tuple[Optional[int], Optional[int]]:
        """Normalize `expand` to `(col_weight, row_weight)`, each `None` or `int >= 0`."""
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
        # Fallback: ignore bad input
        return None, None
