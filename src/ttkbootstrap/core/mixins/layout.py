from __future__ import annotations
from typing import Any
from tkinter import ttk

class LayoutMixin:
    parent: Any
    widget: Any

    def __init__(self, layout: dict | None = None, **_):
        # Only the options relevant to GridBox/grid are tracked here
        self._layout_options = layout or {}

    # --------------------- mounting helpers ---------------------
    def _auto_mount(self):
        """Mount via parent layout if available; otherwise grid-mount."""
        if getattr(self.parent, "add", None):
            self.parent.add(self)
        else:
            self.mount()  # grid by default

    def mount(self, **overrides):
        """Grid-mount with translated options; only 'grid' is supported."""
        opts = self._translate_grid_layout((self._layout_options or {}).copy())
        opts.update(overrides)
        self.widget.grid(**opts)
        return self

    # ---------------------- option plumbing ---------------------
    @staticmethod
    def layout_from_options(kwargs: dict[str, Any] | None) -> dict:
        """Extract grid-relevant layout options from widget kwargs."""
        if not kwargs:
            return {}
        layout: dict[str, Any] = {}
        for k in (
            "sticky", "margin", "padding",
            # grid placement
            "row", "col", "column", "rowspan", "colspan", "offset",
            # direct geometry overrides
            "padx", "pady", "ipadx", "ipady", "expand"
        ):
            if k in kwargs:
                layout[k] = kwargs.pop(k)
        return layout

    # --------------------- grid translation ---------------------
    def _translate_grid_layout(self, layout: dict) -> dict:
        """Translate semantic layout to tkinter.grid() kwargs."""
        opts: dict[str, Any] = {}

        # sticky passes through
        if layout.get("sticky"):
            opts["sticky"] = layout["sticky"]

        # placement (accept both 'col' and 'column')
        if "row" in layout:
            opts["row"] = layout["row"]
        if "col" in layout:
            opts["column"] = layout["col"]
        elif "column" in layout:
            opts["column"] = layout["column"]
        if "rowspan" in layout:
            opts["rowspan"] = layout["rowspan"]
        if "colspan" in layout:
            opts["columnspan"] = layout["colspan"]

        # margin -> outer padding
        margin: list | int = layout.get("margin", 0)
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

        # padding -> internal space for non-Frame widgets
        pad: list | int = layout.get("padding", 0)
        if not isinstance(self.widget, ttk.Frame):
            if isinstance(pad, int):
                opts["ipadx"] = pad
                opts["ipady"] = pad
            elif isinstance(pad, tuple) and len(pad) == 2:
                opts["ipadx"], opts["ipady"] = pad

        # explicit geometry overrides
        for k in ("padx", "pady", "ipadx", "ipady"):
            if k in layout:
                opts[k] = layout[k]

        return opts
