from tkinter import Widget

from typing import NamedTuple


class Geometry(NamedTuple):
    """Widget geometry including size and position."""
    width: int
    height: int
    x: int
    y: int


class WidgetInfoMixin:
    """Provides geometry and visibility information about a widget."""

    widget: Widget

    def geometry(self) -> Geometry:
        """Return widget geometry as width, height, x, and y coordinates."""
        value = self.widget.winfo_geometry()
        size_part, _, pos_part = value.partition('+')
        width_str, _, height_str = size_part.partition('x')
        x_str, _, y_str = pos_part.partition('+')

        return Geometry(
            width=int(width_str),
            height=int(height_str),
            x=int(x_str),
            y=int(y_str),
        )

    def width(self) -> int:
        """Return the widget's current width in pixels."""
        return self.widget.winfo_width() if self.is_mapped() else self.widget.winfo_reqwidth()

    def height(self) -> int:
        """Return the widget's current height in pixels."""
        return self.widget.winfo_height() if self.is_mapped() else self.widget.winfo_reqheight()

    def x_coordinate(self) -> int:
        """Return the widget's x-coordinate relative to its parent."""
        return self.widget.winfo_x()

    def y_coordinate(self) -> int:
        """Return the widget's y-coordinate relative to its parent."""
        return self.widget.winfo_y()

    def exists(self) -> bool:
        """Return True if the widget still exists."""
        return self.widget.winfo_exists()

    def is_mapped(self) -> bool:
        """Return True if the widget is mapped to the screen using a geometry manager (layout)."""
        return self.widget.winfo_ismapped()

    def is_viewable(self) -> bool:
        """Return True if the widget and its ancestors are all mapped."""
        return self.widget.winfo_viewable()

    def widget_class(self) -> str:
        """Return the widget's class name."""
        return self.widget.winfo_class()

    def pixels(self, value: int | str) -> int:
        """Convert a screen distance value to pixels (int)."""
        return self.widget.winfo_pixels(value)

    def float_pixels(self, value: float | str) -> float:
        """Convert a screen distance value to pixels (float)."""
        return self.widget.winfo_fpixels(value)
