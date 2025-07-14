# geometry managers
from tkinter import Misc
from tkinter import Widget
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ttkbootstrap.core.widget import BaseWidget


class GeometryMixin:
    widget: Union["BaseWidget", Widget]

    def pack(self, option=None, **kwargs):
        if option is None:
            self.widget.pack(**kwargs)
            return self
        else:
            return self.widget.pack(option)

    def pack_forget(self):
        self.widget.pack_forget()
        return self
