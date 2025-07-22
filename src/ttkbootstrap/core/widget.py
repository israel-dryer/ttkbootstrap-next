from tkinter import Misc
from typing import TYPE_CHECKING, Union

from .mixins.binding import BindingMixin
from .mixins.configure import ConfigureMixin
from .mixins.focus import FocusMixIn
from .mixins.geometry import GeometryMixin
from .mixins.grab import GrabMixIn
from .mixins.winfo import WidgetInfoMixin

if TYPE_CHECKING:
    from ttkbootstrap.core.app import App


class BaseWidget(
    BindingMixin,
    FocusMixIn,
    GrabMixIn,
    GeometryMixin,
    WidgetInfoMixin,
    ConfigureMixin
):
    _widget: Union["BaseWidget", Misc]

    def __init__(self, parent: Union["BaseWidget", Misc, "App"] = None, **kwargs):
        super().__init__()
        self._parent = parent

        # get surface color
        self._surface_token = kwargs.pop('surface', None)
        self.bind('theme-changed', lambda _: self.update_style())

    @property
    def parent(self):
        return self._parent

    @property
    def widget(self):
        return self._widget

    @property
    def tk(self):
        return self.widget.tk

    @property
    def surface_token(self):
        if self._surface_token is not None:
            return self._surface_token
        else:
            return self._parent.surface_token

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
