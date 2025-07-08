from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.tokens import ForegroundColor, SurfaceColor


class LabelStyleBuilder(StyleBuilderBase):

    def __init__(self, foreground=None, background=None, **kwargs):
        super().__init__("TLabel", foreground=foreground, background=background, **kwargs)

    def foreground(self, value: ForegroundColor = None):
        if value is None:
            return self.options.get('foreground', None)
        else:
            self.options.update(foreground=value)
            return self

    def background(self, value: SurfaceColor = None):
        if value is None:
            return self.options.get('background', None)
        else:
            self.options.update(background=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        foreground_token = self.foreground()
        background_token = self.background()

        if background_token is None:
            background = self.theme.color(surface_token)
        else:
            background = self.theme.color(background_token)

        if foreground_token is None:
            foreground = self.theme.on_color(background)
        else:
            foreground = self.theme.color(foreground_token)
        self.configure(ttk_style, background=background, foreground=foreground)
