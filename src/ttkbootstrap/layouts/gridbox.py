"""
GridBox: a grid-first layout with semantic alignment and smart gaps.

Strategy
--------
`GridBox` is a thin, predictable layer over Tk's `grid` that adds:
  * **Semantic alignment**: fixed-axes mapping like CSS Grid/Flex docs:
      - `justify_*` → horizontal behavior (west/east/we).
      - `align_*`   → vertical behavior (north/south/ns).
    Per-item `justify_self` / `align_self` override container defaults
    `justify_items` / `align_items`. These semantics are translated to a
    `sticky` string only; no track sizing is performed here.
  * **Smart gaps**: symmetric inter-cell spacing by splitting `gap` into
    left/right (columns) and top/bottom (rows), trimming outer edges so the
    grid’s perimeter is not padded unintentionally. Margins are merged on top.
  * **Ergonomic sizing**:
      - `columns` / `rows` accept a list of ints (weights) or fixed strings
        like `"240px"` for minsize. A bare int configures a number of equal
        weighted tracks.
      - `grid_propagate(propagate)` is exposed so you can opt-in/out of geometry
        propagation from children.
  * **Auto layout**: when you omit `row`/`col`, items flow left→right across the
    configured columns and wrap to the next row (simple placement; not flex-wrap).

This keeps the mental model simple: use `GridBox` when you want a classic grid
with cleaner spacing and per-item alignment semantics; use `FlexBox` when you
want flex-like main/cross distribution and item weighting on the main axis.
"""

from __future__ import annotations
from typing import Unpack, Union, TypedDict, Optional, Literal

from ttkbootstrap.core.base_widget_alt import BaseWidget
from ttkbootstrap.layouts.frame import Frame
from ttkbootstrap.layouts.constants import layout_context_stack
from ttkbootstrap.layouts.types import Sticky, SemanticLayoutOptions
from ttkbootstrap.layouts.utils import add_pad, margin_to_pad, normalize_gap, normalize_padding
from ttkbootstrap.style.tokens import SurfaceColor
from ttkbootstrap.widgets.types import FrameOptions

AxisAlign = Literal["start", "end", "center", "stretch"]


class GridLayoutOptions(FrameOptions, total=False):
    """Per-child layout options accepted by :class:`GridBox`."""
    row: int
    col: int
    rowspan: int
    colspan: int
    offset: int
    sticky: Sticky
    padx: int | tuple[int, int]
    pady: int | tuple[int, int]
    # semantic (per-item) – captured by LayoutMixin, used here if sticky not set
    justify_self: AxisAlign
    align_self: AxisAlign


class GridRowOptions(TypedDict, total=False):
    """Row configuration forwarded to `rowconfigure`."""
    weight: int
    height: int


class GridColumnOptions(TypedDict, total=False):
    """Column configuration forwarded to `columnconfigure`."""
    weight: int
    width: int


class _Options(GridLayoutOptions, SemanticLayoutOptions, total=False):
    """Typed options for the GridBox container itself."""
    surface: SurfaceColor
    variant: str


class GridBox(Frame):
    """Grid-first layout with semantic alignment and smart gaps."""

    def __init__(
            self,
            parent=None,
            *,
            gap: int | tuple[int, int] = 0,
            padding: Union[int, tuple[int, int], tuple[int, int, int, int]] = 0,
            columns: int | list[str | int] = 12,
            rows: int | list[str | int] = None,
            propagate: bool = True,
            sticky_content: Sticky = None,
            expand_content: bool = None,
            justify_items: Optional[AxisAlign] = None,
            align_items: Optional[AxisAlign] = None,
            **kwargs: Unpack[_Options]
    ):
        """Initialize a GridBox container.

        GridBox translates fixed-axes semantics into Tk's `grid` options:

        * **Alignment semantics**:
          - `justify_items` / per-item `justify_self` control **horizontal**
            stickiness: "start"→"w", "end"→"e", "center"→"", "stretch"→"we".
          - `align_items` / per-item `align_self` control **vertical**
            stickiness: "start"→"n", "end"→"s", "center"→"", "stretch"→"ns".
          When a child does not provide `sticky`, GridBox synthesizes it from
          these semantics. An explicit `sticky` on the child always wins.

        * **Gaps & margins**:
          - `gap=(col_gap, row_gap)` is split between neighboring cells and
            trimmed on the outer edges. Per-item `margin` (if provided by the
            widget’s LayoutMixin) is merged with the computed gap into `padx/pady`.

        * **Track sizing**:
          - `columns` / `rows` accept either:
              • an integer N → creates N weighted tracks (weight=1), or
              • a list of ints (weights) and/or fixed strings ending with "px"
                (which set `minsize` and weight=0 for that track).
          You can further tweak tracks with `configure_column()` and
          `configure_row()`.

        * **Auto-placement**:
          - If a child omits `row`/`col`, GridBox places it left→right across
            the configured columns, advancing to the next row as needed. The
            optional `offset` adds an extra column offset before placing.

        Args:
            parent: Parent widget.
            gap: Inter-cell spacing as `(col_gap, row_gap)` or a single int
                applied to both; split/trimmed to avoid outer padding.
            padding: Internal padding for the GridBox frame.
            columns: Either an int for N equal-weight columns, or a list with
                per-column weights (ints) and/or fixed widths as strings like
                `"240px"`.
            rows: Optional rows configuration using the same conventions as
                `columns`. When omitted, rows are created on-demand by the
                auto-placer.
            propagate: Whether to enable `grid_propagate` on the container.
            sticky_content: Fallback sticky applied to children that do not
                specify sticky and for which no justify/align semantic is set.
            expand_content: Captured on children as a semantic hint; primarily
                relevant when those children are later packed elsewhere.
            justify_items: Container default horizontal alignment for children
                ("start"|"center"|"end"|"stretch") when they do not set
                `justify_self` and have no explicit `sticky`.
            align_items: Container default vertical alignment for children
                ("start"|"center"|"end"|"stretch") when they do not set
                `align_self` and have no explicit `sticky`.
            **kwargs: Frame styling/layout options (e.g., `surface`, `variant`,
                `margin`, `sticky`, etc.). The container’s own `sticky` is
                passed to `grid` on the container itself via :class:`Frame`.
        """
        self._gap = normalize_gap(gap)
        self._padding = normalize_padding(padding)
        self._columns = columns if isinstance(columns, list) else [1] * columns
        self._rows = rows if isinstance(rows, list) else []
        self._auto_layout = True
        self._next_row = 0
        self._next_col = 0
        self._mounted: dict[BaseWidget, dict] = {}
        self._sticky_content = sticky_content
        self._expand_content = expand_content
        self._justify_items = justify_items
        self._align_items = align_items

        super().__init__(parent, padding=self._padding, **kwargs)
        self.widget.grid_propagate(propagate)

        # Configure columns
        for index, col in enumerate(self._columns):
            if isinstance(col, int):
                self.configure_column(index, weight=col)
            elif isinstance(col, str) and col.endswith("px"):
                self.configure_column(index, weight=0)
                self.widget.grid_columnconfigure(index, minsize=int(col.removesuffix("px")))

        # Configure rows (optional upfront)
        if self._rows:
            for index, row in enumerate(self._rows):
                if isinstance(row, int):
                    self.configure_row(index, weight=row)
                elif isinstance(row, str) and row.endswith("px"):
                    self.configure_row(index, weight=0)
                    self.widget.grid_rowconfigure(index, minsize=int(row.removesuffix("px")))

    def __enter__(self):
        """Enter a layout context so child widgets auto-mount into this GridBox."""
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        """Exit the layout context."""
        layout_context_stack().pop()

    def add(self, widget: BaseWidget):
        """Register and mount a child widget.

        If the child does not provide `sticky`, GridBox synthesizes one from
        `justify_self` / `align_self` or the container defaults.

        Args:
            widget: A widget that follows the LayoutMixin contract.
        """
        layout_options = getattr(widget, "_layout_options", {}).copy()

        # Pass-through semantic expand (primarily for pack elsewhere)
        if self._expand_content is not None and "expand" not in layout_options:
            layout_options["expand"] = self._expand_content

        # Synthesize sticky from semantics if none provided
        if not (layout_options.get("sticky") or "").strip():
            js = layout_options.get("justify_self") or self._justify_items
            as_ = layout_options.get("align_self") or self._align_items
            sticky = self._compute_sticky_from_semantics(js, as_)
            if sticky:
                layout_options["sticky"] = sticky
            elif self._sticky_content:
                layout_options["sticky"] = self._sticky_content

        widget._layout_options = layout_options
        self._add(widget, **layout_options)

    def _add(self, widget: BaseWidget, **options: Unpack[GridLayoutOptions]):
        """Place a child using grid, applying gap/margin padding and auto-placement.

        Args:
            widget: Child widget to position.
            **options: Grid placement and sticky options; supports `row/col`,
                `rowspan/colspan`, `offset`, `sticky`, and padding overrides.
        """
        if self._auto_layout:
            options = self._apply_auto_layout(options)

        col = options.get("col", 0)
        row = options.get("row", 0)
        col_span = options.get("colspan", 1)
        row_span = options.get("rowspan", 1)
        sticky = options.get("sticky", "ew")

        gap_x, gap_y = self._gap

        # Base gap pads centered between cells
        left_pad = gap_x // 2
        right_pad = gap_x - left_pad
        top_pad = gap_y // 2
        bottom_pad = gap_y - top_pad

        # Trim outer edges
        if col == 0:
            left_pad = 0
        if (col + col_span) == len(self._columns):
            right_pad = 0
        if row == 0:
            top_pad = 0

        pad_x = (left_pad, right_pad)
        pad_y = (top_pad, bottom_pad)

        # Merge margin (from LayoutMixin / widget kwargs)
        margin = options.pop("margin", 0)
        m_padx, m_pady = margin_to_pad(margin)
        pad_x = add_pad(pad_x, m_padx)
        pad_y = add_pad(pad_y, m_pady)

        # Merge explicit widget-level padx/pady if provided
        if "padx" in options:
            pad_x = add_pad(pad_x, options["padx"])
        if "pady" in options:
            pad_y = add_pad(pad_y, options["pady"])

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

    def add_all(self, widgets: list[BaseWidget | tuple[BaseWidget, GridLayoutOptions]]):
        """Add multiple children; tuples provide per-child options."""
        for item in widgets:
            if isinstance(item, tuple):
                widget, opts = item
                self._add(widget, **opts)
            else:
                self.add(item)

    def remove(self, widget: BaseWidget):
        """Forget a managed child from the grid tracking."""
        if widget in self._mounted:
            widget.widget.grid_forget()
            del self._mounted[widget]

    def configure_row(self, index: int, **options: Unpack[GridRowOptions]):
        """Forward row configuration to the underlying grid."""
        self.widget.rowconfigure(index, **options)

    def configure_column(self, index: int, **options: Unpack[GridColumnOptions]):
        """Forward column configuration to the underlying grid."""
        self.widget.columnconfigure(index, **options)

    def configure_child(
            self,
            widget: BaseWidget,
            option: str = None,
            **options: Unpack[GridLayoutOptions]
    ):
        """Get or update a managed child’s configuration.

        Args:
            widget: A previously-added child.
            option: If provided, returns the current stored value for this key.
            **options: When `option` is not provided, reapply placement using
                these options.

        Returns:
            The requested option value when `option` is given; otherwise `self`.
        """
        if widget not in self._mounted:
            raise ValueError("Widget is not managed by this layout.")
        if option:
            return self._mounted[widget].get(option)
        else:
            self.remove(widget)
            self._add(widget, **options)
            return self

    def _apply_auto_layout(self, options: GridLayoutOptions) -> GridLayoutOptions:
        """Simple left-to-right auto-placement with wrap to next row.

        Increments internal cursors `_next_col`/`_next_row`. Honors `colspan`
        and an optional `offset` columns before placing.

        Args:
            options: Incoming placement options.

        Returns:
            A completed options dict with `row` and `col` filled in.
        """
        col_span = options.get("colspan", 1)
        offset = options.pop("offset", 0)
        cols = len(self._columns)

        if self._next_col + offset + col_span > cols:
            self._next_row += 1
            self._next_col = 0

        options.setdefault("row", self._next_row)
        options.setdefault("col", self._next_col + offset)
        self._next_col += offset + col_span

        return options

    # ------------------------- helpers -------------------------
    @staticmethod
    def _compute_sticky_from_semantics(justify: Optional[AxisAlign], align: Optional[AxisAlign]) -> Sticky | None:
        """Translate fixed-axes semantics into a `sticky` string.

        Args:
            justify: Horizontal semantic ("start"|"center"|"end"|"stretch").
            align: Vertical semantic ("start"|"center"|"end"|"stretch").

        Returns:
            A Tk `sticky` string like "we", "ns", "nsew", or `None` if both are
            center/unspecified.
        """

        def hmap(v: AxisAlign | None) -> str:
            if v == "start": return "w"
            if v == "end":   return "e"
            if v == "stretch": return "we"
            return ""  # center/None -> no horizontal fill

        def vmap(v: AxisAlign | None) -> str:
            if v == "start": return "n"
            if v == "end":   return "s"
            if v == "stretch": return "ns"
            return ""  # center/None

        h = hmap(justify)
        v = vmap(align)
        sticky = "".join(c for c in "nsew" if c in set(h + v))
        return sticky or None
