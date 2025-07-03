from tkinter import Misc
from typing import TYPE_CHECKING, Union, Any

if TYPE_CHECKING:
    from ttkbootstrap.core.widget import BaseWidget

class ContainerMixin:
    """Mixin that exposes container-related access from widget"""

    widget: Union["BaseWidget", Misc]

    @property
    def master(self):
        return self.widget.master

    @property
    def tk(self):
        return self.widget.tk

    @property
    def _w(self):
        return self.widget._w

    @property
    def _last_child_ids(self):
        return self.widget._last_child_ids

    @_last_child_ids.setter
    def _last_child_ids(self, value):
        self.widget._last_child_ids = value

    @property
    def children(self):
        return self.widget.children