from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.frame import FrameStyleBuilder
from ttkbootstrap.style.tokens import SurfaceTokenType
from tkinter import ttk

class Frame(BaseWidget):

    _configure_methods = {"surface"}

    def __init__(self, parent, surface: SurfaceTokenType = None, variant: str = None, **kwargs):
        self._widget = ttk.Frame(parent, **kwargs)

        self._surface_token = surface
        super().__init__(parent, surface=surface)
        self._style_builder = FrameStyleBuilder(variant=variant)

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

    def surface(self, value=None):
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self._style_builder.surface(value)
            self.update_style()
            return self

