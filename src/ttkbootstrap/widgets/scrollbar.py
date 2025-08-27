from tkinter import ttk
from typing import Callable, Unpack

from ttkbootstrap.common.types import Orientation, CoreOptions
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.style.builders.scrollbar import ScrollbarStyleBuilder


class ScrollbarOptions(CoreOptions, total=False):
    """
    Options for configuring a scrollbar widget.

    Attributes:
        cursor: The cursor that appears when the mouse is over the widget.
        take_focus: Indicates whether the widget accepts focus during keyboard traversal.
    """
    cursor: str
    take_focus: bool
    on_scroll: Callable


class Scrollbar(BaseWidget):
    """A themed scrollbar widget with support for fractional movement and position."""

    widget: ttk.Scrollbar
    _configure_methods = {"on_scroll": "on_scroll"}

    def __init__(
            self,
            orient: Orientation = "vertical",
            on_scroll: Callable = None,
            **kwargs: Unpack[ScrollbarOptions]):
        """
        Initialize a new themed scrollbar.

        Args:
            orient: The widget orientation.
            on_scroll: The `xview` or `yview` method of a scrollable widget
            **kwargs: Additional configuration options.
        """
        self._on_scroll = on_scroll
        self._style_builder = ScrollbarStyleBuilder(orient=orient)

        parent = kwargs.pop("parent", None)
        tk_options = dict(orient=orient, command=on_scroll, **kwargs)
        super().__init__(ttk.Scrollbar, tk_options, parent=parent)

    def on_scroll(self, func: Callable = None):
        """Get or set the on_scroll callback bound to a scrollable widgets (yview, xview)"""
        if func is None:
            return self._on_scroll
        else:
            self._on_scroll = func
            self.widget.configure(command=func)
            return self

    def delta(self, x: int, y: int) -> float:
        """Return the fractional change if the scrollbar were moved by (x, y) pixels."""
        return self.widget.delta(x, y)

    def fraction(self, x: int, y: int) -> float:
        """Return the fractional slider position at pixel coordinates (x, y)."""
        return self.widget.fraction(x, y)

    def get(self) -> tuple[float, float]:
        """Return the (first, last) fractional range of the current slider position."""
        return self.widget.get()

    def set(self, first: float | str, last: float | str):
        """Set the fractional range (first, last) of the slider position (0.0 to 1.0)."""
        self.widget.set(first, last)
