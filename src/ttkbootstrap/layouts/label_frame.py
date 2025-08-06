from typing import Unpack, cast

from ttkbootstrap.common.types import Fill, LabelFrameOptions
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.base_widget import BaseWidget, current_layout, layout_context_stack
from tkinter import ttk

from ttkbootstrap.style.builders.label_frame import LabelFrameStyleBuilder
from ttkbootstrap.style.tokens import BorderColor, ForegroundColor, SurfaceColor
from ttkbootstrap.common.utils import unsnake_kwargs
from ttkbootstrap.layouts.pack_frame import PackLayoutOptions


class LabelFrame(BaseWidget, ContainerMixin):
    """A themed label frame widget with support for surface and color theming,
    style propagation, and layout container behavior.
    """
    _configure_methods = {"border_color", "background", "label_color"}

    def __init__(
            self,
            parent=None,
            text: str = None,
            label_color: ForegroundColor = None,
            background: SurfaceColor = None,
            border_color: BorderColor = None,
            **kwargs: Unpack[LabelFrameOptions]
    ):
        """Create a themed LabelFrame widget.

        Args:
            parent: The parent widget.
            text: The label text shown at the top of the frame.
            label_color: The text color of the label.
            background: The background color of the labelframe.
            border_color: The border color or accent theme token.
            **kwargs: Additional options accepted by the base LabelFrame widget.
        """
        parent = parent or current_layout()
        self._style_builder = LabelFrameStyleBuilder(
            border_color=border_color, label_color=label_color)
        self._widget = ttk.LabelFrame(parent, text=text, **unsnake_kwargs(kwargs))
        super().__init__(parent, surface=background)
        self.update_style()

    def __enter__(self):
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        layout_context_stack().pop()

    def background(self, value: SurfaceColor = None):
        """Get or set the border color for this widget."""
        if value is None:
            return self._style_builder.surface()
        else:
            self._style_builder.surface(value)
            self.update_style()
            return self

    def label_color(self, value: SurfaceColor = None):
        """Get or set the border color for this widget."""
        if value is None:
            return self._style_builder.label_color()
        else:
            self._style_builder.label_color(value)
            self.update_style()
            return self

    def border_color(self, value: BorderColor = None):
        """Get or set the border color for this widget."""
        if value is None:
            return self._style_builder.border_color()
        else:
            self._style_builder.border_color(value)
            self.update_style()
            return self

    def add(self, widget: BaseWidget, **options: Unpack[PackLayoutOptions]):
        """Add widget to the layout"""
        options.setdefault('fill', cast(Fill, 'x'))
        widget.widget.pack(**options)
        return self

    def remove(self, widget: BaseWidget):
        """Remove a widget from the layout"""
        widget.widget.pack_forget()
        return self
