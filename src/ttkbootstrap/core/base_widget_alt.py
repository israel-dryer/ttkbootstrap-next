from tkinter import ttk
from typing import Callable, Literal, cast

from ttkbootstrap.common.utils import unsnake_kwargs
from ttkbootstrap.layouts.constants import current_layout, default_root
from ttkbootstrap.core.mixins.binding import BindingMixin
from ttkbootstrap.core.mixins.configure import ConfigureMixin
from ttkbootstrap.core.mixins.focus import FocusMixIn
from ttkbootstrap.core.mixins.geometry import GeometryMixin
from ttkbootstrap.core.mixins.grab import GrabMixIn
from ttkbootstrap.core.mixins.layout import LayoutMixin
from ttkbootstrap.core.mixins.winfo import WidgetInfoMixin

PositionType = Literal['static', 'absolute', 'fixed']


class BaseWidget(
    BindingMixin,
    FocusMixIn,
    GrabMixIn,
    GeometryMixin,
    WidgetInfoMixin,
    ConfigureMixin,
    LayoutMixin
):
    _widget: ttk.Widget

    def __init__(
            self,
            tk_widget: Callable,
            tk_widget_options: dict = None,
            *,
            auto_mount: bool = True,
            mountable: bool = False,
            parent: "BaseWidget" = None,
            **kwargs):

        self._mountable = mountable
        self._position = tk_widget_options.pop('position', cast(PositionType, 'static'))
        super().__init__()

        # get parent
        if self._position == 'fixed':
            self._parent = default_root()
        else:
            self._parent = parent or current_layout()

        # extract layout options & initialize layout
        layout: dict = BaseWidget.layout_from_options(tk_widget_options)  # type:ignore
        LayoutMixin.__init__(self, layout)

        # initialize tkinter widget
        self._widget: ttk.Widget = tk_widget(self._parent, **(unsnake_kwargs(tk_widget_options) or dict()))

        # re-apply padding if supported (e.g., ttk.Frame)
        if "padding" in layout and isinstance(self._widget, ttk.Frame):
            self._widget.configure(padding=layout["padding"])

        # get surface color
        self._surface_token = kwargs.pop('surface', None)
        self.bind('theme-changed', lambda _: self.update_style())

        # mount the widget to the parent container
        if auto_mount and self.parent.mountable:
            self._auto_mount()
            self._register_and_maybe_sync()

    @property
    def parent(self):
        return self._parent

    @property
    def widget(self) -> ttk.Widget:
        return self._widget

    @property
    def mountable(self):
        return self._mountable

    @property
    def tk(self):
        return self.widget.tk

    @property
    def surface_token(self):
        if self._surface_token is not None:
            return self._surface_token
        else:
            return self._parent.surface_token

    def schedule(self, ms: int, func: Callable, *args):
        return self.widget.after(ms, func, *args)

    def schedule_after_idle(self, func: Callable, *args):
        return self.widget.after_idle(func, *args)

    def schedule_cancel(self, func_id: str):
        return self.widget.after_cancel(func_id)

    def is_ttk(self) -> bool:
        """Check if the underlying widget is a ttk widget.

        Returns:
            True if the widget class name starts with 'T' (e.g., 'TButton'), indicating ttk.
        """
        return self.widget_class().startswith("T")

    def state(self, value: str | list[str] | tuple[str, ...] = None):
        """Get or set the widget state.

        Accepts a single string (e.g. "disabled"), a negated state (e.g. "!selected"),
        or a list/tuple of multiple states (e.g. ["disabled", "readonly"]).
        """
        return self.widget.state(value)

    def destroy(self):
        """Destroy and unregister the widget."""
        self.widget.destroy()

    def update_style(self):
        """Apply theme styling"""
        if hasattr(self, "_style_builder"):
            self._style_builder.surface(self.surface_token)
            style_name = self._style_builder.build()
            if "tkinter" in style_name:
                pass
            else:
                self.configure(style=style_name)

    def __str__(self):
        return str(self.widget)
