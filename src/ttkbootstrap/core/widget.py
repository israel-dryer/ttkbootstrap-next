from tkinter import Misc
from typing import Union

from .mixins.binding import BindingMixin
from .mixins.configure import ConfigureMixin
from .mixins.focus import FocusMixIn
from .mixins.grab import GrabMixIn
from .mixins.winfo import WidgetInfoMixin


class BaseWidget(
    BindingMixin,
    FocusMixIn,
    GrabMixIn,
    WidgetInfoMixin,
    ConfigureMixin
):
    _widget: "BaseWidget"

    def __init__(self, parent: Union["BaseWidget", Misc]):
        self._parent = parent
        super().__init__()

    @property
    def widget(self):
        return self._widget

    @property
    def tk(self):
        return self.widget.tk

    def __str__(self):
        return str(self.widget)
