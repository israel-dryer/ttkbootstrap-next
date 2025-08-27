from tkinter import ttk
from typing import Unpack, Literal, Union

from ttkbootstrap.common.types import Orientation, CoreOptions
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.style.builders.separator import SeparatorStyleBuilder
from ttkbootstrap.style.types import SemanticColor

SeparatorColor = Union[Literal['border'], SemanticColor]


class SeparatorOptions(CoreOptions, total=False): ...


class Separator(BaseWidget):
    """A themed horizontal or vertical line used to divide content areas."""

    widget: ttk.Separator
    _configure_methods = {"color": "color", "orient": "orient"}

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
            kwargs: Other widget options.
        """
        self._style_builder = SeparatorStyleBuilder(color, orient)
        parent = kwargs.pop('parent', None)
        tk_options = {**kwargs, "orient": orient}
        super().__init__(ttk.Separator, tk_options, parent=parent)

    def color(self, value: SeparatorColor = None):
        """Get or set the separator color."""
        if value is None:
            return self._style_builder.color()
        else:
            self._style_builder.color(value)
            self.update_style()
            return self

    def orient(self, value: Orientation = None):
        """Get or set the separator orientation."""
        if value is None:
            return self.configure('orient')
        else:
            self.configure(orient=value)
            self._style_builder.orient(value)
            self.update_style()
            return self
