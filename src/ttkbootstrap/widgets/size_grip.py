from typing import Unpack

from ttkbootstrap.widgets.types import SizeGripOptions
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.layouts.constants import current_layout
from ttkbootstrap.style.builders.size_grip import SizeGripStyleBuilder
from ttkbootstrap.style.tokens import SemanticColor
from tkinter import ttk

from ttkbootstrap.common.utils import unsnake_kwargs


class SizeGrip(BaseWidget):
    """A themed size grip widget with support for dynamic color styling.

    This class wraps `ttk.Sizegrip` and allows setting a theme-aware color
    using ttkbootstrap token values. Style updates are applied dynamically
    via the `StyleBuilder` system.
    """

    def __init__(self, parent=None, color: SemanticColor = None, **kwargs: Unpack[SizeGripOptions]):
        """Initialize a new SizeGrip widget.

        Args:
            parent: The parent widget.
            color: The color token to apply to the sizegrip element.
            **kwargs: Additional ttk.Sizegrip configuration options.
        """
        parent = parent or current_layout()
        self._style_builder = SizeGripStyleBuilder(color)
        self._widget = ttk.Sizegrip(parent, **unsnake_kwargs(kwargs))
        super().__init__(parent)
        self.update_style()

    def color(self, value: SemanticColor = None):
        """Get or set the sizegrip color."""
        if value is None:
            return self._style_builder.color()
        else:
            self._style_builder.color(value)
            self.update_style()
            return self
