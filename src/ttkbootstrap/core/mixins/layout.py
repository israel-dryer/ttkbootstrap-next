from __future__ import annotations
from typing import Any, Literal, TYPE_CHECKING, TypedDict, Unpack
from tkinter import ttk

if TYPE_CHECKING:
    from ttkbootstrap.core.base_widget_alt import BaseWidget


class PlacePositionOptions(TypedDict, total=False):
    x: int | str
    y: int | str
    width: int | str
    height: int | str
    anchor: str
    border_mode: Literal['inside', 'outside'] = 'inside'
    container: "BaseWidget"


class LayoutMixin:
    parent: Any
    widget: Any
    _position: Literal['static', 'absolute', 'fixed']

    def __init__(self, layout: dict | None = None, **_):
        # Only the options relevant to GridBox/grid are tracked here
        self._layout_options = layout or {}

    # --------------------- mounting helpers ---------------------
    def _auto_mount(self):
        """Mount via parent layout if available; otherwise grid-mount."""
        if self._position != 'static':
            return  # user is placing this widget manually
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

    def place(self, **kwargs: Unpack[PlacePositionOptions]):
        """
        Position the widget using the Tkinter `place` geometry manager.

        This method extends Tkinter's `place()` by adding:

        - **Percentage-based coordinates and sizes**:
          Values for `x`, `y`, `width`, and `height` may be given as either
          integers (pixels) or strings ending with '%' (e.g. `"50%"`), which are
          converted to relative values (`relx`, `rely`, `relwidth`, `relheight`).

        - **Automatic container resolution**:
          If a `container` keyword is provided, it will be used as the `in_`
          parameter to `place()` (accepts either a `BaseWidget` or a Tk widget).
          Otherwise:
            * For `position='fixed'`, the widget is placed relative to its
              toplevel window (via `.winfo_toplevel()`).
            * For all other positions, placement is relative to `self.parent`.

        - **Border mode translation**:
          The `border_mode` keyword (Literal["inside", "outside"]) is translated
          to Tk's `bordermode` option.

        Args:
            **kwargs: Placement options. In addition to standard Tk `place()` options,
                supports:
                - `x`, `y` (int | str[%])
                - `width`, `height` (int | str[%])
                - `anchor` (str)
                - `border_mode` (Literal["inside", "outside"])
                - `container` (BaseWidget | tk.Misc)

        Example:
            ```python
            btn.place(x="50%", y=10, width="25%", height=40, anchor="n")
            ```
            Places the widget horizontally centered at y=10px, with a width equal
            to 25% of the container's width.
        """
        # 1) Extract & remove non-Tk options up front
        container = kwargs.pop("container", None)
        border_mode = kwargs.pop("border_mode", None)  # we’ll translate to 'bordermode'

        # 2) Translate percent-based values
        options = LayoutMixin._translate_place_options(**kwargs)

        # 3) Apply container / in_
        options |= self._identify_place_container(container)

        # 4) Fix option name for Tk
        if border_mode is not None:
            options["bordermode"] = border_mode

        self.widget.place(**options)
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

    @staticmethod
    def _relative_value(key, value):
        if isinstance(value, int):
            return {key: value}
        else:
            return {f'rel{key}': float(value.replace('%', '')) / 100}

    @staticmethod
    def _translate_place_options(**kwargs):
        opts = kwargs.copy()

        def rel(key, value):
            if isinstance(value, int):
                return {key: value}
            # Expect strings like "75%"
            return {f"rel{key}": float(value.replace("%", "")) / 100.0}

        if "width" in opts:
            v = opts.pop("width")
            opts |= rel("width", v)
        if "height" in opts:
            v = opts.pop("height")
            opts |= rel("height", v)
        if "x" in opts:
            v = opts.pop("x")
            opts |= rel("x", v)
        if "y" in opts:
            v = opts.pop("y")
            opts |= rel("y", v)
        return opts

    def _identify_place_container(self, container):
        # Use explicit container if provided
        if container is not None:
            # Accept either a BaseWidget or a tk widget
            try:
                tk_container = getattr(container, "widget", container)
            except Exception:
                tk_container = container
            return {"in_": tk_container}

        # Otherwise decide by position mode
        if self._position == "fixed":
            # Use the actual toplevel, not the literal "."
            return {"in_": self.widget.winfo_toplevel()}
        else:
            return {"in_": getattr(self, "parent", None)}
