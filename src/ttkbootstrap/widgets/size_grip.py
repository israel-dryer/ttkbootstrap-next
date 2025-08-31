from typing import Unpack

from ttkbootstrap.types import CoreOptions
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.style.builders.size_grip import SizeGripStyleBuilder
from tkinter import ttk

from ttkbootstrap.style.types import SemanticColor


class SizeGripOptions(CoreOptions, total=False):
    """Optional keyword arguments accepted by the `SizeGrip` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the widget.
        take_focus: Specifies if the widget accepts focus during keyboard traversal.
    """
    cursor: str
    take_focus: bool


class SizeGrip(BaseWidget):
    """A themed size grip widget with support for dynamic color styling.

    This class wraps `ttk.Sizegrip` and allows setting a theme-aware color
    using ttkbootstrap token values. Style updates are applied dynamically
    via the `StyleBuilder` system.
    """

    widget: ttk.Sizegrip
    _configure_methods = {"color": "color"}

    def __init__(self, color: SemanticColor = None, **kwargs: Unpack[SizeGripOptions]):
        """Initialize a new SizeGrip widget.

        Args:
            color: The color token to apply to the sizegrip element.
            **kwargs: Additional ttk.Sizegrip configuration options.
        """
        self._style_builder = SizeGripStyleBuilder(**{'color': color} if color else {})
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
