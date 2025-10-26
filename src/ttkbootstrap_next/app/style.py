from tkinter import Tk

from ttkbootstrap_next.style import StyleManager
from ttkbootstrap_next.types import Widget


class WindowStyleBuilder(StyleManager):

    def __init__(self, window: Widget, **kwargs):
        super().__init__("tkinter", **kwargs)
        self._window: Tk = window
        self.options.set_defaults(surface="background", variant="default")

    @property
    def window(self):
        return self._window


@WindowStyleBuilder.register_variant("default")
def build_default_window_style(b: WindowStyleBuilder):
    surface_token = b.options("surface")
    background = b.color(surface_token)
    b.window.configure(background=background)
