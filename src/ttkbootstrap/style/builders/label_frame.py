from ttkbootstrap.style.builders.base import StyleBuilderBase


class LabelFrameStyleBuilder(StyleBuilderBase):

    def __init__(self, color: str = None):
        super().__init__("TLabelframe", color=color)

    def color(self, value: str = None):
        if value is None:
            return self.options.get('color', 'primary')
        else:
            self.options.update(color=value)
            return self

    def surface(self, value: str = None):
        if value is None:
            return self._surface
        else:
            self._surface = value
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        background = self.theme.surface_color(self.surface())
        foreground = self.theme.on_surface(self.surface())
        color = self.color()
        if color is None:
            border = self.theme.border_on_surface(background)
        else:
            border = self.theme.foreground_color(color)
        self.configure(
            ttk_style,
            background=background,
            bordercolor=border,
            lightcolor=background,
            darkcolor=background
        )
        self.configure(f"{ttk_style}.Label", foreground=foreground, background=background)
