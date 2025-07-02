from typing import TYPE_CHECKING

from .base import StyleBuilderBase

if TYPE_CHECKING:
    from ttkbootstrap.core.widget import BaseWidget

class WindowStyleBuilder(StyleBuilderBase):

    def __init__(self, window: "BaseWidget", **kwargs):
        super().__init__("tkinter", **kwargs)
        self._window = window

    @property
    def window(self):
        return self._window

    def surface(self, value: str = None):
        if value is None:
            return self._surface
        else:
            self._surface = value
            return self

    def register_style(self):
        background = self.theme.surface_color(self.surface())

        self.window.configure(background=background)
