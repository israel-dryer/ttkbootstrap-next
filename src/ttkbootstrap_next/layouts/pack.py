import tkinter as tk
from tkinter import ttk
from typing import Literal, Optional, Unpack, cast

from ttkbootstrap_next.core.layout_context import pop_container, push_container
from ttkbootstrap_next.layouts.base_layout import BaseLayout
from ttkbootstrap_next.layouts.types import FrameOptions
from ttkbootstrap_next.types import Anchor, Fill, Padding, Side


class PackOptions(FrameOptions, total=False):
    surface: str
    variant: str


class Pack(BaseLayout):
    widget: ttk.Frame

    def __init__(
            self,
            *,
            direction: Literal["horizontal", "vertical", "row", "column", "row-reverse", "column-reverse"] = "vertical",
            gap: int = 0,
            padding: Padding = 0,
            propagate: Optional[bool] = None,
            expand_items: Optional[bool] = None,
            fill_items: Optional[Fill] = None,
            anchor_items: Optional[Anchor] = None,
            **kwargs: Unpack[PackOptions],
    ):
        super().__init__(**kwargs)
        self._direction = direction
        self._gap = gap
        self._padding = padding
        self._propagate = propagate
        self._expand_items = expand_items
        self._fill_items = fill_items
        self._anchor_items = anchor_items

        self._side_map = {
            "vertical": "top",
            "column": "top",
            "column-reverse": "bottom",
            "horizontal": "left",
            "row": "left",
            "row-reverse": "right",
        }
        if self._propagate is not None:
            self.widget.pack_propagate(self._propagate)
        self.widget.configure(padding=self._padding)

    # Lightweight context (no queueing)
    def __enter__(self):
        push_container(self)
        return self

    def __exit__(self, exc_type, exc, tb):
        pop_container()

    # --- Guidance only: compute side/gaps/defaults; do NOT mount ------
    def guide_layout(self, child, method: str, options: dict) -> tuple[str, dict]:
        # Only advise pack; otherwise pass-through.
        if method and method != "pack":
            return method, dict(options or {})
        method = "pack"

        opts = dict(options or {})
        side = opts.get("side")
        if side not in ("top", "bottom", "left", "right", "center"):
            side = cast(Side, self._side_map.get(self._direction, "top"))

        # Count only siblings already managed by pack
        siblings = [
            c for c in self.widget.winfo_children()
            if isinstance(c, tk.Widget) and c.winfo_manager() == "pack"
        ]
        is_first = (len(siblings) == 0)

        guided: dict[str, object] = {"side": side}

        # Apply directional gap only for non-first sibling
        if not is_first and self._gap:
            if self._direction in ("vertical", "column"):
                guided.setdefault("pady", (self._gap, 0))
            elif self._direction == "column-reverse":
                guided.setdefault("pady", (0, self._gap))
            elif self._direction in ("horizontal", "row"):
                guided.setdefault("padx", (self._gap, 0))
            elif self._direction == "row-reverse":
                guided.setdefault("padx", (0, self._gap))

        # Container-level defaults
        if self._expand_items is not None:
            guided.setdefault("expand", self._expand_items)
        if self._fill_items is not None:
            guided.setdefault("fill", self._fill_items)
        if self._anchor_items is not None:
            guided.setdefault("anchor", self._anchor_items)

        # Child options win in the child's attach; here we merge to preview
        merged = {**guided, **opts}
        return method, merged

    def preferred_layout_method(self) -> str:
        return "pack"
