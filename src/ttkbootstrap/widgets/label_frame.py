from typing import Unpack

from ttkbootstrap.core.libtypes import LabelFrameOptions
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.widget import BaseWidget
from tkinter import ttk

from ttkbootstrap.style.builders.label_frame import LabelFrameStyleBuilder
from ttkbootstrap.style.tokens import ForegroundToken, SurfaceToken, ThemeColorToken
from ttkbootstrap.utils import unsnake_kwargs


class LabelFrame(BaseWidget, ContainerMixin):
    """A themed label frame widget with support for surface and color theming,
    style propagation, and layout container behavior.
    """
    _configure_methods = {"surface", "border_color"}

    def __init__(
            self,
            parent,
            text: str = None,
            surface: SurfaceToken = None,
            border_color: ForegroundToken = None,
            **kwargs: Unpack[LabelFrameOptions]
    ):
        """Create a themed LabelFrame widget.

        Args:
            parent: The parent widget.
            text: The label text shown at the top of the frame.
            surface: The background theme token to apply to the frame.
            border_color: The border color or accent theme token.
            **kwargs: Additional options accepted by the base LabelFrame widget.
                See `LabelFrameOptions` for details.
        """

        self._style_builder = LabelFrameStyleBuilder(color=border_color)
        self._widget = ttk.LabelFrame(parent, text=text, **unsnake_kwargs(kwargs))
        super().__init__(parent, surface=surface)

    def surface(self, value=None):
        """Get or set the surface token for this widget."""
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self._style_builder.surface(value)
            self.update_style()
            return self

    def border_color(self, value=None):
        """Get or set the border color for this widget."""
        if value is None:
            return self._style_builder.color()
        else:
            self._style_builder.color(value)
            self.update_style()
            return self
