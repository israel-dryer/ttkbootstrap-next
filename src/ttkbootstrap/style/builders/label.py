from ttkbootstrap.style.builders.base import StyleBuilderBase


class LabelStyleBuilder(StyleBuilderBase):

    def __init__(self, foreground: str = None, background: str = None, **kwargs):
        super().__init__("TLabel", foreground=foreground, background=background, **kwargs)

    def foreground(self, value: str = None):
        if value is None:
            return self.options.get('foreground', None)
        else:
            self.options.update(foreground=value)
            return self

    def background(self, value: str = None):
        if value is None:
            return self.options.get('background', None)
        else:
            self.options.update(background=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        background = self.theme.surface_color(self.background() or self.surface())
        foreground_token = self.foreground()
        if foreground_token is None:
            foreground = self.theme.on_surface(self.background() or self.surface())
        else:
            foreground = self.theme.foreground_color(foreground_token)
        self.configure(ttk_style, background=background, foreground=foreground)
