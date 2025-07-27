from typing import Unpack

from ttkbootstrap.core.libtypes import LabelFrameOptions
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.widget import BaseWidget
from tkinter import ttk

from ttkbootstrap.style.builders.label_frame import LabelFrameStyleBuilder
from ttkbootstrap.style.tokens import BorderColor, ForegroundColor, SurfaceColor
from ttkbootstrap.utils import unsnake_kwargs


class LabelFrame(BaseWidget, ContainerMixin):
    """A themed label frame widget with support for surface and color theming,
    style propagation, and layout container behavior.
    """
    _configure_methods = {"border_color", "background", "label_color"}

    def __init__(
            self,
            parent,
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

        self._style_builder = LabelFrameStyleBuilder(
            border_color=border_color, label_color=label_color)
        self._widget = ttk.LabelFrame(parent, text=text, **unsnake_kwargs(kwargs))
        super().__init__(parent, surface=background)
        self.update_style()

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
