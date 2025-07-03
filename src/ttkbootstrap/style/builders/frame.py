from ttkbootstrap.style.builders.base import StyleBuilderBase


class FrameStyleBuilder(StyleBuilderBase):

    def __init__(self, variant: str = None, **kwargs):
        super().__init__("TFrame", variant=variant, **kwargs)

    def surface(self, value: str = None):
        if value is None:
            return self._surface
        else:
            self._surface = value
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        background = self.theme.surface_color(self.surface())
        self.configure(ttk_style, background=background)
