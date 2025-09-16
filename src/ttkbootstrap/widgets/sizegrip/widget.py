from tkinter import ttk
from typing import Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.widgets.sizegrip.style import SizegripStyleBuilder
from ttkbootstrap.style.types import SemanticColor
from ttkbootstrap.widgets.sizegrip.types import SizegripOptions


class Sizegrip(BaseWidget):
    """A themed size grip widget with support for dynamic color styling.

    This class wraps `ttk.Sizegrip` and allows setting a theme-aware color
    using ttkbootstrap token values. Style updates are applied dynamically
    via the `StyleBuilder` system.
    """

    widget: ttk.Sizegrip
    _configure_methods = {"color": "color"}

    def __init__(self, color: SemanticColor = None, **kwargs: Unpack[SizegripOptions]):
        """Initialize a new SizeGrip widget.

        Args:
            color: The color token to apply to the sizegrip element.
            **kwargs: Additional ttk.Sizegrip configuration options.
        """
        self._style_builder = SizegripStyleBuilder(**{'color': color} if color else {})
        parent = kwargs.pop('parent', None)
        tk_options = dict(**kwargs)
        super().__init__(ttk.Sizegrip, tk_options, parent=parent)

    def color(self, value: SemanticColor = None):
        """Get or set the sizegrip color."""
        if value is None:
            return self._style_builder.options('color')
        else:
            self._style_builder.options(color=value)
            self.update_style()
            return self


SizeGrip = Sizegrip
