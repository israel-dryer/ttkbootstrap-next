from ttkbootstrap.style.builders.base import StyleBuilderBase


class LabelFrameStyleBuilder(StyleBuilderBase):

    def __init__(self, border_color: str = None, label_color: str = None):
        super().__init__(
            "TLabelframe",
            border_color=border_color,
            label_color=label_color
        )

    def border_color(self, value: str = None):
        if value is None:
            return self.options.get('border_color', None)
        else:
            self.options.update(border_color=value)
            return self

    def label_color(self, value: str = None):
        if value is None:
            return self.options.get('label_color', None)
        else:
            self.options.update(label_color=value)
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
        surface = self.theme.surface_color(self.surface())
        border_token = self.border_color()
        if border_token is None:
            border = self.theme.border_on_surface(surface)
        else:
            border = self.theme.foreground_color(border_token)
        self.configure(
            ttk_style,
            background=background,
            bordercolor=border,
            lightcolor=background,
            darkcolor=background
        )
        self.configure(f"{ttk_style}.Label", foreground=foreground, background=surface)
