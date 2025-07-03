from ttkbootstrap.style.builders.base import StyleBuilderBase


class LabelStyleBuilder(StyleBuilderBase):

    def __init__(self, color: str = None, **kwargs):
        super().__init__("TLabel", color=color, **kwargs)

    def color(self, value: str = None):
        if value is None:
            return self.options.get('color', None)
        else:
            self.options.update(color=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        background = self.theme.surface_color(self.surface())
        color = self.color()
        if color is None:
            foreground = self.theme.on_surface(self.surface())
        else:
            foreground = self.theme.foreground_color(color)
        self.configure(ttk_style, background=background, foreground=foreground)
