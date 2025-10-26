from tkinter import ttk
from typing import Unpack

from ttkbootstrap_next.core.base_widget import BaseWidget
from ttkbootstrap_next.interop.runtime.configure import configure_delegate
from ttkbootstrap_next.style.types import SemanticColor
from ttkbootstrap_next.widgets.sizegrip.style import SizegripStyleBuilder
from ttkbootstrap_next.widgets.sizegrip.types import SizegripOptions


class Sizegrip(BaseWidget):
    """A themed size grip widget with support for dynamic color styling.

    This class wraps `ttk.Sizegrip` and allows setting a theme-aware color
    using ttkbootstrap token values. Style updates are applied dynamically
    via the `StyleBuilder` system.
    """

    widget: ttk.Sizegrip

    def __init__(self, color: SemanticColor = None, **kwargs: Unpack[SizegripOptions]):
        """Initialize a new SizeGrip widget.

        Args:
            color: The color token to apply to the sizegrip element.

        Keyword Args:
            cursor: Mouse cursor to display when hovering over the widget.
            id: A unique identifier used to query this widget.
            parent: The parent container of this widget.
            take_focus: Specifies if the widget accepts focus during keyboard traversal.
        """
        self._style_builder = SizegripStyleBuilder(**{'color': color} if color else {})
        parent = kwargs.pop('parent', None)
        tk_options = dict(**kwargs)
        super().__init__(ttk.Sizegrip, tk_options, parent=parent)

    @configure_delegate("color")
    def _configure_color(self, value: SemanticColor = None):
        """Get or set the sizegrip color."""
        if value is None:
            return self._style_builder.options('color')
        else:
            self._style_builder.options(color=value)
            self.update_style()
            return self


SizeGrip = Sizegrip
