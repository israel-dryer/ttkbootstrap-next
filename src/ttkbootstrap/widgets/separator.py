from tkinter import ttk

from ttkbootstrap.core.libtypes import Orient
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.separator import SeparatorStyleBuilder
from ttkbootstrap.style.tokens import SeparatorColorToken


class Separator(BaseWidget):
    """A themed horizontal or vertical line used to divide content areas."""

    _configure_methods = {"color", "orient"}

    def __init__(self, parent, color: SeparatorColorToken = "border", orient: Orient = "horizontal"):
        """
        Initialize a Separator widget.

        Args:
            parent: The parent widget.
            color: The separator color token (e.g., "border", "primary").
            orient: Orientation of the separator ("horizontal" or "vertical").
        """
        self._style_builder = SeparatorStyleBuilder(color, orient)
        self._widget = ttk.Separator(parent, orient=orient)
        super().__init__(parent)

    def color(self, value: SeparatorColorToken = None):
        """Get or set the separator color."""
        if value is None:
            return self._style_builder.color()
        else:
            self._style_builder.color(value)
            self.update_style()
            return self

    def orient(self, value: Orient = None):
        """Get or set the separator orientation."""
        if value is None:
            return self.configure('orient')
        else:
            self.configure(orient=value)
            self._style_builder.orient(value)
            self.update_style()
            return self
