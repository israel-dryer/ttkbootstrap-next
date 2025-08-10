"""
FlexBox: a flexbox-like layout built on Tk's grid using spacer tracks.

Strategy
--------
This layout emulates CSS Flexbox using a single-row/column "content band" and
dedicated spacer tracks:

* Axes: `direction` defines MAIN vs CROSS axes (row→main=h, column→main=v).
  - `justify_*` affects the MAIN axis.
  - `align_*`   affects the CROSS axis.
* Distribution:
  - MAIN axis spacing uses interior/outer spacer tracks (grid columns or rows).
  - `justify_content="stretch"` gives weight to *item tracks* on MAIN axis,
    using each child's `weight` (default 1; 0 = no expansion).
  - Other MAIN modes distribute weight on spacers instead.
  - On the CROSS axis, `align_content` manipulates only the *content band*:
      - `stretch` gives the content band weight to fill the cross axis.
      - `start`/`end`/`center` position the band via outer spacers.
      - (No wrapping: `space-between`/`space-around` collapse to `center`.)
* Gaps: `gap` sets `minsize` on interior spacers along the MAIN axis only.
* Placement: children are placed at every other index (1,3,5,...) in the
  content band; no wrapping is performed.

This design keeps Tk geometry predictable, avoids direct per-widget geometry
options leaking in, and mirrors Flexbox semantics closely without adding
wrapping complexity.
"""

from __future__ import annotations
from typing import Literal, Unpack, Optional, cast

from ttkbootstrap.layouts.frame import Frame
from ttkbootstrap.core.base_widget_alt import BaseWidget
from ttkbootstrap.layouts.constants import layout_context_stack
from ttkbootstrap.layouts.utils import margin_to_pad
from ttkbootstrap.layouts.types import SemanticLayoutOptions, Sticky
from ttkbootstrap.widgets.types import FrameOptions
from ttkbootstrap.style.tokens import SurfaceColor


class _Options(FrameOptions, SemanticLayoutOptions, total=False):
    """Typed options for FlexBox container widgets."""
    surface: SurfaceColor
    variant: str


JustifyContent = Literal[
    "start", "end", "center", "space-between", "space-around", "stretch"
]
AlignContent = Literal["start", "end", "center", "stretch"]

AxisAlign = Literal["start", "end", "center", "stretch"]
Direction = Literal["row", "row-reverse", "column", "column-reverse"]


class FlexBox(Frame):
    """Flexbox-like layout using grid with spacer tracks (single line)."""

    def __init__(
            self,
            parent=None,
            *,
            direction: Direction = "row",
            gap: int | tuple[int, int] = 0,
            justify_content: JustifyContent = "start",
            align_content: AlignContent = "start",
            justify_items: Optional[AxisAlign] = None,
            align_items: Optional[AxisAlign] = None,
            propagate: bool = True,
            **kwargs: Unpack[_Options],
    ):
        """Initialize a FlexBox container.

        This container arranges children along a MAIN axis (defined by
        `direction`) and positions the entire content band along the CROSS axis.
        MAIN-axis spacing is implemented with spacer tracks; when
        `justify_content="stretch"`, item tracks receive weights from each
        child's `weight` layout option (default 1; 0 means no expansion) while
        spacers remain at weight 0. CROSS-axis placement/stretching manipulates
        only the single content band (no wrapping).

        Args:
            parent: Parent widget.
            direction: Flow direction and MAIN axis:
                - "row"/"row-reverse": MAIN = horizontal, CROSS = vertical.
                - "column"/"column-reverse": MAIN = vertical, CROSS = horizontal.
            gap: Space between adjacent items along the MAIN axis. An int applies
                to the MAIN axis; a 2-tuple applies (horizontal, vertical) with
                only the MAIN component used for spacer minsize.
            justify_content: MAIN-axis distribution. In "stretch" mode, item
                tracks get weights from each child `weight`; otherwise spacers
                receive weight per the chosen mode.
            align_content: CROSS-axis distribution of the single content band.
                Without wrapping, "space-between"/"space-around" behave as
                "center". "stretch" gives the content band weight to fill.
            justify_items: Default per-item alignment on the MAIN axis
                ("start"/"end"/"center"/"stretch") when an item does not specify
                `justify_self`.
            align_items: Default per-item alignment on the CROSS axis
                ("start"/"end"/"center"/"stretch") when an item does not specify
                `align_self`.
            propagate: Whether to allow the container's grid to propagate size
                from children (`grid_propagate`).
            **kwargs: Frame styling/layout options (e.g., `surface`, `variant`,
                `padding`, `margin`, `sticky`, etc.). If `sticky` is omitted,
                the container defaults to `"nsew"`.

        Notes:
            - Child-level layout options consumed by FlexBox include:
              `weight` (int >= 0), `justify_self`, `align_self`, and `margin`.
            - Container-level defaults `justify_items`/`align_items` are used
              when an item does not set its own `justify_self`/`align_self`.
        """
        if "sticky" not in kwargs:
            kwargs["sticky"] = "nsew"

        super().__init__(parent, **kwargs)

        self._direction: Direction = direction
        self._gap = (gap, gap) if isinstance(gap, int) else gap
        self._justify_content = justify_content
        self._align_content = align_content
        self._justify_items = justify_items
        self._align_items = align_items
        self._children: list[BaseWidget] = []

        self.widget.grid_propagate(propagate)
        self._ensure_axis_scaffolds()

    # ------------------------ context manager ------------------------
    def __enter__(self):
        """Enter a layout context so child widgets auto-mount into this container."""
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        """Exit the layout context."""
        layout_context_stack().pop()

    # ------------------------- public API ---------------------------
    def add(self, widget: BaseWidget):
        """Register and mount a child widget into the FlexBox."""
        opts = getattr(widget, "_layout_options", {}).copy()
        opts.setdefault("__direction", self._direction)

        # margins → padx/pady
        margin = opts.pop("margin", 0)
        padx_m, pady_m = margin_to_pad(margin)

        # if caller provided sticky, use it; otherwise synthesize from semantics
        explicit = (opts.get("sticky") or "").strip()
        if explicit:
            sticky = cast(Sticky, explicit)
        else:
            sticky = self._compute_item_sticky(opts)

        widget._layout_options = opts
        self._children.append(widget)
        self._relayout()

        i = self._children.index(widget)
        row, col = self._row_col_for_index(i, len(self._children))
        widget.mount("grid", row=row, column=col, padx=padx_m, pady=pady_m, sticky=sticky)
        return self

    # ------------------------ layout helpers ------------------------
    def _is_row(self) -> bool:
        """Return True if MAIN axis is horizontal."""
        return self._direction.startswith("row")

    def _gap_on_main(self) -> int:
        """Return the effective gap value for the MAIN axis."""
        return self._gap[0] if self._is_row() else self._gap[1]

    def _ensure_axis_scaffolds(self):
        """Initialize CROSS-axis scaffold rows/columns for the content band."""
        if self._is_row():
            for r in range(3):
                self.widget.rowconfigure(r, weight=0, minsize=0)
        else:
            for c in range(3):
                self.widget.columnconfigure(c, weight=0, minsize=0)

    def _relayout(self):
        """(Re)build spacer and item tracks and apply axis distributions."""
        n = len(self._children)
        if n == 0:
            return

        if self._is_row():
            total_cols = 2 * n + 1
            gap = self._gap_on_main()
            for c in range(total_cols):
                is_spacer = (c % 2 == 0)
                interior = 0 < c < total_cols - 1
                self.widget.columnconfigure(c, minsize=(gap if is_spacer and interior else 0), weight=0)

            for i, child in enumerate(self._children):
                col = self._place_index(i, n)
                child.widget.grid(row=1, column=col)

            self._apply_justify_main(total_tracks=total_cols)
            self._apply_align_cross_for_row_direction()

        else:
            total_rows = 2 * n + 1
            gap = self._gap_on_main()
            for r in range(total_rows):
                is_spacer = (r % 2 == 0)
                interior = 0 < r < total_rows - 1
                self.widget.rowconfigure(r, minsize=(gap if is_spacer and interior else 0), weight=0)

            for i, child in enumerate(self._children):
                row = self._place_index(i, n)
                child.widget.grid(row=row, column=1)

            self._apply_justify_main(total_tracks=total_rows)
            self._apply_align_cross_for_column_direction()

    # ---------------- MAIN axis distribution (justify_*) -------------
    def _apply_justify_main(self, *, total_tracks: int):
        """Apply MAIN-axis distribution (items vs spacers) according to `justify_content`."""
        if self._is_row():
            for c in range(total_tracks):
                self.widget.columnconfigure(c, weight=0)
        else:
            for r in range(total_tracks):
                self.widget.rowconfigure(r, weight=0)

        n = len(self._children)

        if self._justify_content == "stretch":
            # items get weights; spacers stay 0
            for i, child in enumerate(self._children):
                idx = self._place_index(i, n)
                raw = child._layout_options.get("weight")
                w = self._parse_weight(raw)
                w = 1 if w is None else w
                if self._is_row():
                    self.widget.columnconfigure(idx, weight=w)
                else:
                    self.widget.rowconfigure(idx, weight=w)
            return

        first, last = 0, total_tracks - 1
        interior_spacers = list(range(2, total_tracks - 1, 2))

        def set_spacer(idx: int, w: int):
            if self._is_row():
                self.widget.columnconfigure(idx, weight=w)
            else:
                self.widget.rowconfigure(idx, weight=w)

        match self._justify_content:
            case "start":
                set_spacer(last, 1)
            case "end":
                set_spacer(first, 1)
            case "center":
                set_spacer(first, 1);
                set_spacer(last, 1)
            case "space-between":
                for s in interior_spacers:
                    set_spacer(s, 1)
            case "space-around":
                for s in range(0, total_tracks, 2):
                    set_spacer(s, 1)
            case _:
                pass

    # ---------------- CROSS axis distribution (align_*) --------------
    def _apply_align_cross_for_row_direction(self):
        """CROSS axis for row direction: operate on 3 rows (top/content/bottom)."""
        for r in range(3):
            self.widget.rowconfigure(r, weight=0)

        match self._align_content:
            case "stretch":
                self.widget.rowconfigure(1, weight=1)
            case "start":
                self.widget.rowconfigure(2, weight=1)
            case "end":
                self.widget.rowconfigure(0, weight=1)
            case "center" | "space-between" | "space-around":
                self.widget.rowconfigure(0, weight=1)
                self.widget.rowconfigure(2, weight=1)
            case _:
                pass

    def _apply_align_cross_for_column_direction(self):
        """CROSS axis for column direction: operate on 3 columns (left/content/right)."""
        for c in range(3):
            self.widget.columnconfigure(c, weight=0)

        match self._align_content:
            case "stretch":
                self.widget.columnconfigure(1, weight=1)
            case "start":
                self.widget.columnconfigure(2, weight=1)
            case "end":
                self.widget.columnconfigure(0, weight=1)
            case "center" | "space-between" | "space-around":
                self.widget.columnconfigure(0, weight=1)
                self.widget.columnconfigure(2, weight=1)
            case _:
                pass

    # ----------------------- index helpers ---------------------------
    def _place_index(self, i: int, n: int) -> int:
        """Return the MAIN-axis grid index (row/column) for the i-th item."""
        idx = 2 * i + 1
        if self._direction.endswith("-reverse"):
            last_item_pos = 2 * (n - 1) + 1
            idx = last_item_pos - 2 * i
        return idx

    def _row_col_for_index(self, i: int, n: int) -> tuple[int, int]:
        """Return (row, column) target for the i-th item in the content band."""
        if self._is_row():
            return (1, self._place_index(i, n))
        else:
            return (self._place_index(i, n), 1)

    # ------------------------- sticky logic -------------------------
    def _compute_item_sticky(self, opts: dict) -> Sticky:
        """Map per-item justify/align to sticky on MAIN/CROSS axes."""
        justify_self: Optional[AxisAlign] = opts.get("justify_self")
        align_self: Optional[AxisAlign] = opts.get("align_self")

        justify = justify_self or self._justify_items or "stretch"
        align = align_self or self._align_items or "stretch"

        if self._is_row():
            h = self._axis_to_sticky(justify, main_is_horizontal=True)
            v = self._axis_to_sticky(align, main_is_horizontal=False)
        else:
            v = self._axis_to_sticky(justify, main_is_horizontal=False)
            h = self._axis_to_sticky(align, main_is_horizontal=True)

        sticky = "".join(sorted(set(h + v)))
        order = "nsew"
        sticky = "".join([c for c in order if c in sticky])
        return cast(Sticky, sticky or "")

    def _axis_to_sticky(self, val: AxisAlign, *, main_is_horizontal: bool) -> str:
        """Translate axis-aligned value to a sticky string segment."""
        if main_is_horizontal:
            match val:
                case "start":
                    return "w"
                case "end":
                    return "e"
                case "center":
                    return ""
                case "stretch":
                    return "we"
        else:
            match val:
                case "start":
                    return "n"
                case "end":
                    return "s"
                case "center":
                    return ""
                case "stretch":
                    return "ns"
        return ""

    # --------------------------- utils ------------------------------
    @staticmethod
    def _parse_weight(value) -> int | None:
        """Return None if not provided; else int >= 0 (None → default share=1)."""
        if value is None:
            return None
        try:
            w = int(value)
            return w if w >= 0 else 0
        except Exception:
            return 0
