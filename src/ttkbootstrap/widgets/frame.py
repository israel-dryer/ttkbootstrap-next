from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.frame import FrameStyleBuilder
from ttkbootstrap.style.tokens import SurfaceTokenType
from tkinter import ttk


class Frame(BaseWidget, ContainerMixin):
    """
    A themed container widget using ttk.Frame with support for surface
    styling and layout composition.
    """

    _configure_methods = {"surface"}

    def __init__(self, parent, surface: SurfaceTokenType = None, variant: str = None, **kwargs):
        """
        Initialize a new themed Frame widget.

        Args:
            parent: The parent widget.
            surface: The surface token to apply (e.g., 'layer01').
            variant: An optional style variant (e.g., 'bordered').
            **kwargs: Additional keyword arguments passed to ttk.Frame.
        """
        self._widget = ttk.Frame(parent, **kwargs)

        self._surface_token = surface
        super().__init__(parent, surface=surface)
        self._style_builder = FrameStyleBuilder(variant=variant)

    def surface(self, value=None):
        """Get or set the surface token for this widget."""
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self._style_builder.surface(value)
            self.update_style()
            return self
