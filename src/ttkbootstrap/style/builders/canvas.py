import tkinter

from ttkbootstrap.style.builders.base import StyleBuilderBase


class CanvasStyleBuilder(StyleBuilderBase):

    def __init__(self, canvas: tkinter.Canvas, **kwargs):
        super().__init__("tkinter", **kwargs)
        self._canvas = canvas

    @property
    def canvas(self):
        return self._canvas

    def surface(self, value: str = None):
        if value is None:
            return self._surface
        else:
            self._surface = value
            return self

    def register_style(self):
        background = self.theme.color(self.surface())
        border = self.theme.border(background)
        self.canvas.configure(background=background, highlightbackground=border)
