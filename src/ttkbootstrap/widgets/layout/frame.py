from typing import Unpack

from ttkbootstrap.core.libtypes import FrameOptions
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.frame import FrameStyleBuilder
from ttkbootstrap.style.tokens import SurfaceColor
from tkinter import ttk

from ttkbootstrap.utils import unsnake_kwargs


class Frame(BaseWidget, ContainerMixin):
    """
    A themed container widget using ttk.Frame with support for surface
    styling and layout composition.
    """

    _configure_methods = {"surface"}

    def __init__(
            self,
            parent,
            *,
            surface: SurfaceColor = None,
            variant: str = None,
            **kwargs: Unpack[FrameOptions]):
        """
        Initialize a new themed Frame widget.

        Args:
            parent: The parent widget.
            surface: The surface token to apply (e.g., 'layer01').
            variant: An optional style variant (e.g., 'bordered').
            **kwargs: Additional keyword arguments passed to ttk.Frame.
        """
        build_options = kwargs.pop('builder', dict())
        self._surface_token = surface
        self._widget = ttk.Frame(parent, **unsnake_kwargs(kwargs))
        super().__init__(parent, surface=surface)
        self._style_builder = FrameStyleBuilder(variant=variant, **build_options)

    def surface(self, value: SurfaceColor=None):
        """Get or set the surface token for this widget."""
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self._style_builder.surface(value)
            self.update_style()
            return self
