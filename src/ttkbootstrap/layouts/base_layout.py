from tkinter import ttk
from typing import Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.layouts.style import FrameStyleBuilder
from ttkbootstrap.layouts.types import FrameOptions
from ttkbootstrap.types import Widget
from ttkbootstrap.utils import merge_build_options, unsnake_kwargs


class BaseLayout(BaseWidget, ContainerMixin):
    """
    Base class for layout containers.

    Key points in the immediate-attach architecture:
    - Parents DO NOT mount children.
    - Parents may offer layout *guidance* via guide_layout(child, method, options).
    - Children execute their own geometry manager using the merged options.
    """
    widget: ttk.Frame
    _configure_methods = {"surface": "surface"}

    def __init__(self, *, surface: str = None, variant: str = None, **kwargs: Unpack[FrameOptions]):
        self._surface_token = surface

        style_options = merge_build_options(kwargs.pop("builder", {}), variant=variant)
        style_options["border"] = kwargs.pop("border", None)

        parent = kwargs.pop("parent", None)
        tk_options = unsnake_kwargs(kwargs)
        super().__init__(ttk.Frame, tk_options, parent=parent, surface=surface)
        self._style_builder = FrameStyleBuilder(**style_options)

    # --- Parental guidance hook (no-op by default) --------------------
    def guide_layout(self, child, method: str, options: dict) -> tuple[str, dict]:
        """
        Suggest (method, options) for the child's attach() call.
        Must NOT call any geometry manager here.
        Default: pass-through.
        """
        return method, dict(options or {})

    # Optional helper for place (used by some containers if needed)
    def _mount_child_place(self, child, opts: dict) -> None:
        parent: Widget = self.widget
        tk = getattr(child, "widget", child)
        tk.place(
            in_=parent,
            **{
                k: v
                for k, v in opts.items()
                if k in {
                    "x", "y", "relx", "rely",
                    "width", "height", "relwidth", "relheight",
                    "anchor", "bordermode",
                }
            },
        )

    def surface(self, value: str = None):
        """Get or set the surface (background) color of this widget"""
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self._style_builder.surface_token(value)
            return self

    def preferred_layout_method(self) -> str:
        """Default preferred geometry for bare frames: pack."""
        return "pack"
