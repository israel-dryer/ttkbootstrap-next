from tkinter import Misc
from typing import Union

from .mixins.binding import BindingMixin
from .mixins.configure import ConfigureMixin
from .mixins.focus import FocusMixIn
from .mixins.geometry import GeometryMixin
from .mixins.grab import GrabMixIn
from .mixins.winfo import WidgetInfoMixin


class BaseWidget(
    BindingMixin,
    FocusMixIn,
    GrabMixIn,
    GeometryMixin,
    WidgetInfoMixin,
    ConfigureMixin
):
    _widget: Union["BaseWidget", Misc]

    def __init__(self, parent: Union["BaseWidget", Misc]):
        self._parent = parent
        super().__init__()

    @property
    def widget(self):
        return self._widget

    @property
    def tk(self):
        return self.widget.tk

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
            if not self.is_ttk():
                # background = self._style_builder.surface_color(self._layer)
                # self.option(background=background)
                pass
            else:
                # self._style_builder.level(self.layer)
                # self._style_builder.theme(self.theme.name)
                # style_name = self._style_builder.build()
                # self.option(style=style_name)
                pass

    # def _get_background_color(self):
    #     from tkinter.ttk import Style
    #     style = Style()
    #     if self.is_ttk():
    #         ttk_style = self.widget.configure('background')
    #         return style.configure(ttk_style, 'background')
    #     else:
    #         return self.widget.configure('background')

    def __str__(self):
        return str(self.widget)
