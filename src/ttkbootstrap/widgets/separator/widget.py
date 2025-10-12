from tkinter import ttk
from typing import Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.types import Orientation
from ttkbootstrap.widgets.separator.style import SeparatorStyleBuilder
from ttkbootstrap.widgets.separator.types import SeparatorColor, SeparatorOptions


# TODO add a `thickness` style property

class Separator(BaseWidget):
    """A themed horizontal or vertical line used to divide content areas."""

    widget: ttk.Separator
    _configure_methods = {
        "color": "_configure_color",
        "orient": "_configure_orient"
    }

    def __init__(
            self,
            color: SeparatorColor = "border",
            orient: Orientation = "horizontal",
            **kwargs: Unpack[SeparatorOptions]):
        """
        Initialize a Separator widget.

        Args:
            color: The separator color token (e.g., "border", "primary").
            orient: Orientation of the separator ("horizontal" or "vertical").

        Keyword Args:
            id: A unique identifier used to query this widget.
            parent: The parent container of this widget.
        """
        self._style_builder = SeparatorStyleBuilder(color=color, orient=orient)
        parent = kwargs.pop('parent', None)
        tk_options = {**kwargs, "orient": orient}
        super().__init__(ttk.Separator, tk_options, parent=parent)

    def _configure_color(self, value: SeparatorColor = None):
        if value is None:
            return self._style_builder.options("color")
        else:
            self._style_builder.options(color=value)
            self.update_style()
            return self

    def _configure_orient(self, value: Orientation = None):
        if value is None:
            return self.configure('orient')
        else:
            self.configure(orient=value)
            self._style_builder.options(orient=value)
            self.update_style()
            return self
