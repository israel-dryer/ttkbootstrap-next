from __future__ import annotations
from typing import Any
from tkinter import ttk
from ttkbootstrap.layouts.types import LayoutMethod

class LayoutMixin:
    parent: Any
    widget: Any

    def __init__(self, layout: dict | None = None, **_):
        # semantic + geometry options captured here; containers may read these
        self._layout_options = layout or {}

    # --------------------- mounting helpers ---------------------
    def _auto_mount(self):
        """Mount via parent layout if available; otherwise self-mount.
        Containers (e.g., PackFrame/FlexboxFrame/GridFrame) typically implement
        `.add(child)` and will translate margin/gap/padding. If no such parent
        exists, we translate and mount directly here.
        """
        if getattr(self.parent, "add", None):
            self.parent.add(self)
        else:
            self.mount()

    def mount(self, method: LayoutMethod = "pack", **overrides):
        method = method.lower()
        # Translate semantic layout -> geometry-manager options
        opts = self._translate_layout(method)
        # Explicit call-site overrides win
        opts.update(overrides)

        match method:
            case "pack":
                self.widget.pack(**opts)
            case "grid":
                self.widget.grid(**opts)
            case "place":
                self.widget.place(**opts)
        return self

    # ---------------------- option plumbing ---------------------
    @staticmethod
    def layout_from_options(kwargs: dict[str, Any] | None) -> dict:
        """Pop known layout-related keys off `kwargs` and return them.
        Keeps the widget constructors tidy while preserving semantics for
        translation during mount or by a container.
        """
        if not kwargs:
            return {}
        layout: dict[str, Any] = {}
        for k in (
            # shared semantic keys (geometry-agnostic)
            "sticky", "expand", "margin", "padding",
            # grid semantics
            "row", "column", "rowspan", "colspan",
            # pack semantics
            "side", "anchor",
            # flexbox semantics (must NOT reach tk widget options)
            "justify_self", "align_self", "justify_items", "align_items", "weight",
            # unified growth (consumed by FlexboxFrame)
            "grow",
            # internal seeds some containers may set
            "__direction",
            # direct geometry options that callers may specify explicitly
            "padx", "pady", "ipadx", "ipady",
        ):
            if k in kwargs:
                layout[k] = kwargs.pop(k)
        return layout

    # --------------------- translation core ---------------------
    def _translate_layout(self, method: str) -> dict:
        layout = (self._layout_options or {}).copy()
        if method == "pack":
            return self._translate_pack_layout(layout)
        if method == "grid":
            return self._translate_grid_layout(layout)
        return {}

    @staticmethod
    def _parse_sticky(sticky: str | None) -> tuple[set[str], str | None]:
        """Map `sticky` to pack's (fill, anchor).
        Returns (fills, anchor) where fills is a set like {"x", "y"}.
        """
        if not sticky:
            return set(), None
        s = sticky.lower()
        if s == "center":
            return set(), "center"
        fills: set[str] = set()
        if "e" in s and "w" in s:
            fills.add("x")
        if "n" in s and "s" in s:
            fills.add("y")
        anchor = ""
        if "y" not in fills:
            if "n" in s:
                anchor += "n"
            elif "s" in s:
                anchor += "s"
        if "x" not in fills:
            if "w" in s:
                anchor += "w"
            elif "e" in s:
                anchor += "e"
        if not anchor and "center" in s:
            anchor = "center"
        return fills, (anchor or None)

    def _translate_pack_layout(self, layout: dict) -> dict:
        opts: dict[str, Any] = {}

        # Determine side from explicit override or semantic direction seed
        direction = layout.get("__direction", "row")
        opts["side"] = layout.get("side") or {
            "row": "left",
            "row-reverse": "right",
            "column": "top",
            "column-reverse": "bottom",
        }.get(direction, "left")

        # sticky -> fill/anchor
        fills, anchor = self._parse_sticky(layout.get("sticky"))
        if "x" in fills and "y" in fills:
            opts["fill"] = "both"
        elif "x" in fills:
            opts["fill"] = "x"
        elif "y" in fills:
            opts["fill"] = "y"
        if anchor and opts.get("fill") != "both":
            opts["anchor"] = anchor

        # expand (only if explicitly provided)
        if "expand" in layout:
            opts["expand"] = bool(layout["expand"])

        # margin -> outer padding (padx/pady)
        margin = layout.get("margin", 0)
        if isinstance(margin, int):
            opts["padx"] = margin
            opts["pady"] = margin
        elif isinstance(margin, tuple):
            if len(margin) == 2:
                opts["padx"], opts["pady"] = margin
            elif len(margin) == 4:
                # pack only understands scalar/tuple; containers can refine.
                # Here we approximate by using horizontal/vertical pairs.
                l, t, r, b = margin
                opts["padx"] = (l, r)
                opts["pady"] = (t, b)

        # padding -> internal padding for non-frame widgets
        pad = layout.get("padding", 0)
        if not isinstance(self.widget, ttk.Frame):
            if isinstance(pad, int):
                opts["ipadx"] = pad
                opts["ipady"] = pad
            elif isinstance(pad, tuple) and len(pad) == 2:
                opts["ipadx"], opts["ipady"] = pad

        # Allow direct geometry pads to pass through if user set them
        for k in ("padx", "pady", "ipadx", "ipady"):
            if k in layout:
                opts[k] = layout[k]

        return opts

    def _translate_grid_layout(self, layout: dict) -> dict:
        opts: dict[str, Any] = {}

        # sticky passes through directly for grid
        if layout.get("sticky"):
            opts["sticky"] = layout["sticky"]

        # grid coordinates
        if "row" in layout:
            opts["row"] = layout["row"]
        if "column" in layout:
            opts["column"] = layout["column"]
        if "rowspan" in layout:
            opts["rowspan"] = layout["rowspan"]
        if "colspan" in layout:
            opts["columnspan"] = layout["colspan"]

        # margin -> outer padding around the cell
        margin = layout.get("margin", 0)
        if isinstance(margin, int):
            opts["padx"] = margin
            opts["pady"] = margin
        elif isinstance(margin, tuple):
            if len(margin) == 2:
                opts["padx"], opts["pady"] = margin
            elif len(margin) == 4:
                l, t, r, b = margin
                opts["padx"] = (l, r)
                opts["pady"] = (t, b)

        # padding -> internal padding
        pad = layout.get("padding", 0)
        if not isinstance(self.widget, ttk.Frame):
            if isinstance(pad, int):
                opts["ipadx"] = pad
                opts["ipady"] = pad
            elif isinstance(pad, tuple) and len(pad) == 2:
                opts["ipadx"], opts["ipady"] = pad

        # Allow explicit geometry pads to override translation
        for k in ("padx", "pady", "ipadx", "ipady"):
            if k in layout:
                opts[k] = layout[k]

        return opts
