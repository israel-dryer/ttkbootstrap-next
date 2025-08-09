from __future__ import annotations
from typing import Literal, Unpack

from ttkbootstrap.layouts.types import SemanticLayoutOptions, Sticky
from ttkbootstrap.layouts.frame import Frame
from ttkbootstrap.core.base_widget_alt import BaseWidget
from ttkbootstrap.layouts.constants import layout_context_stack
from ttkbootstrap.layouts.utils import add_pad, margin_to_pad
from ttkbootstrap.style.tokens import SurfaceColor
from ttkbootstrap.widgets.types import FrameOptions


class _Options(FrameOptions, SemanticLayoutOptions, total=False):
    surface: SurfaceColor
    variant: str


class PackFrame(Frame):
    def __init__(
            self,
            parent=None,
            *,
            direction: Literal["row", "row-reverse", "column", "column-reverse"] = "row",
            gap: int | tuple[int, int] = 0,
            propagate: bool = True,
            sticky_content: Sticky = None,
            expand_content: bool = None,
            **kwargs: Unpack[_Options],
    ):
        # Seed smart layout defaults early so they're extracted correctly
        # if "expand" not in kwargs and expand_content is not None:
        #     kwargs["expand"] = expand_content

        if "sticky" not in kwargs:
            if direction.startswith("row"):
                kwargs["sticky"] = "ns"
            elif direction.startswith("column"):
                kwargs["sticky"] = "ew"

        super().__init__(parent, **kwargs)
        self._direction = direction
        self._gap = (gap, gap) if isinstance(gap, int) else gap
        self._sticky_content = sticky_content
        self._expand_content = expand_content
        self._mounted: dict[BaseWidget, dict] = {}

        # propagate?
        self.widget.pack_propagate(propagate)

    def __enter__(self):
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        layout_context_stack().pop()

    def add(self, widget: BaseWidget):
        layout_options = getattr(widget, "_layout_options", {}).copy()
        layout_options.setdefault("__direction", self._direction)

        # Inject container-level defaults if not set
        if self._expand_content is not None and "expand" not in layout_options:
            layout_options["expand"] = self._expand_content

        if self._sticky_content and not layout_options.get("sticky", "").strip():
            layout_options["sticky"] = self._sticky_content

        # Set back updated layout
        widget._layout_options = layout_options

        # Determine pack side
        default_side = {
            "row": "left",
            "row-reverse": "right",
            "column": "top",
            "column-reverse": "bottom"
        }[self._direction]
        side = layout_options.get("side", default_side)

        # Gap logic
        pad_x, pad_y = self._gap
        is_horizontal = side in ("left", "right")
        base_padx = (pad_x, 0) if is_horizontal and self._mounted else 0
        base_pady = (pad_y, 0) if not is_horizontal and self._mounted else 0

        # Margin logic
        margin: tuple | int = layout_options.pop("margin", 0)
        m_padx, m_pady = margin_to_pad(margin)
        final_padx = add_pad(base_padx, m_padx)
        final_pady = add_pad(base_pady, m_pady)

        widget._layout_options = layout_options
        overrides = {"side": side, "padx": final_padx, "pady": final_pady}

        widget.mount("pack", **overrides)

        self._mounted[widget] = overrides
        return self
