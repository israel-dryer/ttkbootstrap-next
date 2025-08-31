from tkinter import ttk
from typing import TypedDict, Unpack

from ttkbootstrap.types import Padding, Widget, Position
from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.utils import merge_build_options, unsnake_kwargs
from ttkbootstrap.style.builders.frame import FrameStyleBuilder


class FrameOptions(TypedDict, total=False):
    """Optional keyword arguments accepted by the `Frame` widget.

    Attributes:
        cursor: Mouse cursor to display when hovering over the frame.
        height: The height of the frame in pixels.
        padding: Space around the frame content.
        take_focus: Specifies if the frame accepts focus during keyboard traversal.
        width: The width of the frame in pixels.
        builder: key-value options passed to the style builder
    """
    cursor: str
    height: int
    padding: Padding
    take_focus: bool
    width: int
    builder: dict
    parent: Widget
    position: Position


class BaseLayout(BaseWidget, ContainerMixin):
    widget: ttk.Frame
    _configure_methods = {"surface": "surface"}

    def __init__(self, *, surface: str = None, variant: str = None, **kwargs: Unpack[FrameOptions]):
        self._surface_token = surface

        style_options = merge_build_options(
            kwargs.pop('builder', {}),
            variant=variant
        )

        parent = kwargs.pop('parent', None)
        tk_options = unsnake_kwargs(kwargs)
        super().__init__(ttk.Frame, tk_options, parent=parent, surface=surface)
        self._style_builder = FrameStyleBuilder(**style_options)

    # Mount a 'place' child directly on this container (no overlay)
    def _mount_child_place(self, child, opts: dict) -> None:
        parent = self.widget
        if hasattr(child, "_attach_place"):
            getattr(child, '_attach_place')(parent, **opts)
        elif hasattr(child, "attach_place"):
            child.attach_place(parent=parent, **opts)
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
