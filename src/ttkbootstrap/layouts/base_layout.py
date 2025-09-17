from tkinter import ttk
from typing import Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.layouts.style import FrameStyleBuilder
from ttkbootstrap.layouts.types import FrameOptions
from ttkbootstrap.types import Widget
from ttkbootstrap.utils import merge_build_options, unsnake_kwargs


class BaseLayout(BaseWidget, ContainerMixin):
    widget: ttk.Frame
    _configure_methods = {"surface": "surface"}

    def __init__(self, *, surface: str = None, variant: str = None, **kwargs: Unpack[FrameOptions]):
        self._surface_token = surface

        style_options = merge_build_options(kwargs.pop('builder', {}), variant=variant)
        style_options['border'] = kwargs.pop('border', None)

        parent = kwargs.pop('parent', None)
        tk_options = unsnake_kwargs(kwargs)
        super().__init__(ttk.Frame, tk_options, parent=parent, surface=surface)
        self._style_builder = FrameStyleBuilder(**style_options)

    # Mount a 'place' child directly on this container (no overlay)
    def _mount_child_place(self, child, opts: dict) -> None:
        parent: Widget = self.widget
        if hasattr(child, "_attach_place"):
            getattr(child, '_attach_place')(parent, **opts)
        elif hasattr(child, "attach_place"):
            child.attach_place(parent=parent.tk_name, **opts)
        else:
            tk = getattr(child, "widget", child)
            tk.place(
                in_=parent, **{k: v for k, v in opts.items() if k in {
                    "x", "y", "relx", "rely", "width", "height", "relwidth", "relheight", "anchor", "bordermode"
                }})

    def surface(self, value: str = None):
        """Get or set the surface (background) color of this widget"""
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self._style_builder.surface(value)
            return self

    def preferred_layout_method(self) -> str:
        """Return the container’s preferred layout method."""
        return "pack"
