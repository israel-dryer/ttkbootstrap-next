from __future__ import annotations
from typing import Any
from tkinter import Tk
from tkinter import ttk
from ttkbootstrap.layouts.types import LayoutMethod

class LayoutMixin:
    parent: Any
    widget: Any

    def __init__(self, layout: dict = None, **_):
        self._layout_options = layout or {}

    def _auto_mount(self):
        if getattr(self.parent, "add", None):
            self.parent.add(self)
        else:
            self.mount()
            #self.widget.place(relwidth=1, relheight=1)

    def mount(self, method: LayoutMethod = "pack", **overrides):

        method = method.lower()
        opts = self._translate_layout(method)

        # Remove semantic-only keys
        for key in (
            "sticky", "margin", "padding", "row", "column",
            "rowspan", "colspan", "side", "anchor"
        ):
            opts.pop(key, None)

        opts |= overrides

        match method:
            case "pack":
                self.widget.pack(**opts)
            case "grid":
                self.widget.grid(**opts)
            case "place":
                self.widget.place(**opts)

        return self

    @staticmethod
    def layout_from_options(kwargs: dict[str, Any]) -> dict:
        layout = {}
        for k in (
            "sticky", "expand", "margin", "padding",
            "row", "column", "rowspan", "colspan",
            "side", "padx", "pady", "ipadx", "ipady", "anchor"
        ):
            if k in kwargs:
                layout[k] = kwargs.pop(k)
        return layout

    def _translate_layout(self, method: str) -> dict:
        layout = self._layout_options.copy()
        if method == "pack":
            return self._translate_pack_layout(layout)
        elif method == "grid":
            return self._translate_grid_layout(layout)
        return {}

    @staticmethod
    def _parse_sticky(sticky: str) -> tuple[set[str], str | None]:
        """Converts `sticky` syntax to a (`fill`, `anchor`) syntax used in the pack manager."""
        if not sticky:
            return set(), None
        s = sticky.lower()
        if s == "center":
            return set(), "center"

        # fill 'x' and 'y' correspond to sticky 'ew' an 'ns'
        fills = set()
        if "e" in s and "w" in s: fills.add("x")
        if "n" in s and "s" in s: fills.add("y")

        # anchors only have an effect when there is space remaining on the axis; i.e. not filled.
        anchors = ""
        if "y" not in fills:
            if "n" in s: anchors += "n"
            elif "s" in s: anchors += "s"
        if "x" not in fills:
            if "w" in s: anchors += "w"
            elif "e" in s: anchors += "e"
        if not anchors and "center" in s:
            anchors = "center"

        return fills, anchors or None

    def _translate_pack_layout(self, layout: dict) -> dict:
        opts = {}
        direction = layout.get("__direction", "row")

        opts["side"] = layout.get("side") or {
            "row": "left", "row-reverse": "right",
            "column": "top", "column-reverse": "bottom"
        }.get(direction, "left")

        # Translate sticky
        fills, anchor = self._parse_sticky(layout.get("sticky", ""))
        if "x" in fills and "y" in fills:
            opts["fill"] = "both"
        elif "x" in fills:
            opts["fill"] = "x"
        elif "y" in fills:
            opts["fill"] = "y"

        if anchor and opts.get("fill") != "both":
            opts["anchor"] = anchor

        # Only include expand if explicitly set
        if "expand" in layout:
            opts["expand"] = bool(layout["expand"])

        # Padding → internal widget space for leaf widgets
        pad: tuple | int = layout.get("padding", 0)
        if not isinstance(self.widget, ttk.Frame):
            # frame handles padding internally, all else use the ipadx/y option
            if isinstance(pad, int):
                opts["ipadx"] = pad
                opts["ipady"] = pad
            elif isinstance(pad, tuple) and len(pad) == 2:
                opts["ipadx"], opts["ipady"] = pad

        return opts

    @staticmethod
    def _translate_grid_layout(layout: dict) -> dict:
        opts = {}

        # Sticky
        if "sticky" in layout:
            opts["sticky"] = layout["sticky"]

        # Grid coordinates
        for k in ("row", "column", "rowspan", "colspan"):
            if k in layout:
                opts["columnspan" if k == "colspan" else k] = layout[k]

        # Padding → internal space
        pad: tuple | int = layout.get("padding", 0)
        if isinstance(pad, int):
            opts["ipadx"] = pad
            opts["ipady"] = pad
        elif isinstance(pad, tuple) and len(pad) == 2:
            opts["ipadx"], opts["ipady"] = pad

        return opts
