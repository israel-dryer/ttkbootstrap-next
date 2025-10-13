import tkinter

from ttkbootstrap.style import StyleManager


class CanvasStyleBuilder(StyleManager):

    def __init__(self, canvas: tkinter.Canvas, **kwargs):
        super().__init__("tkinter", **kwargs)
        self._canvas = canvas
        self.options.set_defaults(variant="default")

    @property
    def canvas(self):
        """Reference to the Canvas instance"""
        return self._canvas


@CanvasStyleBuilder.register_variant("default")
def build_default_canvas_style(b: CanvasStyleBuilder):
    background = b.color(b.surface_token)
    border = b.border(background)
    b.canvas.configure(background=background, highlightbackground=border)
