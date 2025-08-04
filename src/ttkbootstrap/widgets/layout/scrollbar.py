from tkinter import ttk
from typing import Unpack

from ttkbootstrap.core.libtypes import ScrollbarOptions, Orient
from ttkbootstrap.core.widget import BaseWidget, current_layout
from ttkbootstrap.style.builders.scrollbar import ScrollbarStyleBuilder
from ttkbootstrap.utils import unsnake_kwargs


class Scrollbar(BaseWidget):
    """A themed scrollbar widget with support for fractional movement and position."""

    _configure_methods = {}

    def __init__(self, parent=None, orient: Orient="vertical", **kwargs: Unpack[ScrollbarOptions]):
        """
        Initialize a new themed scrollbar.

        Args:
            parent: The parent widget.
            **kwargs: Configuration options for the ttk.Scrollbar widget.
        """
        parent = parent or current_layout()
        self._style_builder = ScrollbarStyleBuilder(orient=orient)
        self._widget = ttk.Scrollbar(parent, orient=orient, **unsnake_kwargs(kwargs))
        super().__init__(parent)
        self.update_style()

    def delta(self, x: int, y: int) -> float:
        """Return the fractional change if the scrollbar were moved by (x, y) pixels."""
        return self.widget.delta(x, y)

    def fraction(self, x: int, y: int) -> float:
        """Return the fractional slider position at pixel coordinates (x, y)."""
        return self.widget.fraction(x, y)

    def get(self) -> tuple[float, float]:
        """Return the (first, last) fractional range of the current slider position."""
        return self.widget.get()

    def set(self, first: float, last: float):
        """Set the fractional range (first, last) of the slider position (0.0 to 1.0)."""
        self.widget.set(first, last)
