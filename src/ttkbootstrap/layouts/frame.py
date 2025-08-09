from typing import Unpack

from ttkbootstrap.layouts.types import SemanticLayoutOptions
from ttkbootstrap.widgets.types import FrameOptions
from ttkbootstrap.core.base_widget_alt import BaseWidget
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.style.builders.frame import FrameStyleBuilder
from ttkbootstrap.style.tokens import SurfaceColor
from tkinter import ttk

from ttkbootstrap.common.utils import unsnake_kwargs


class _Options(FrameOptions, SemanticLayoutOptions):
    pass


class Frame(BaseWidget, ContainerMixin):
    """
    A themed container widget using ttk.Frame with support for surface
    styling and layout composition.
    """

    _configure_methods = {"surface"}

    def __init__(
            self,
            parent=None,
            *,
            surface: SurfaceColor = None,
            variant: str = None,
            **kwargs: Unpack[_Options]):
        """
        Initialize a new themed Frame widget.

        Args:
            parent: The parent widget.
            surface: The surface token to apply (e.g., 'layer01').
            variant: An optional style variant (e.g., 'bordered').
            **kwargs: Additional keyword arguments passed to ttk.Frame.
        """
        self._surface_token = surface
        style_options = kwargs.pop('builder', dict())
        tk_options = unsnake_kwargs(kwargs)

        super().__init__(ttk.Frame, tk_options, parent=parent, surface=surface, auto_mount=True)
        self._style_builder = FrameStyleBuilder(variant=variant, **style_options)

    def surface(self, value: SurfaceColor = None):
        """Get or set the surface token for this widget."""
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self._style_builder.surface(value)
            self.update_style()
            return self
