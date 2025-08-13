from tkinter import Widget, ttk
from typing import Union


class ContainerMixin:
    """Mixin that exposes container-related access from widget"""

    widget: ttk.Widget

    @property
    def master(self):
        return self.widget.master

    @property
    def tk(self):
        return self.widget.tk

    @property
    def _w(self) -> str:
        """The tcl window id"""
        return self.widget._w

    @property
    def _last_child_ids(self) -> list[str]:
        """A list of child ids"""
        return self.widget._last_child_ids

    @_last_child_ids.setter
    def _last_child_ids(self, value: list[str]):
        self.widget._last_child_ids = value

    @property
    def children(self) -> dict[str, Union[ttk.Widget, Widget]]:
        """A list of child widgets"""
        return self.widget.children
