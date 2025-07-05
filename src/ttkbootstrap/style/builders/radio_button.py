from ttkbootstrap.style.builders.base import StyleBuilderBase


class RadioButtonStyleBuilder(StyleBuilderBase):

    def __init__(self, color):

        super().__init__('TRadiobutton', color=color)

    def color(self, value: str = None):
        if value is None:
            return self.options.get('color', 'primary')
        else:
            self.options.update(color=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        background = self.theme.surface_color(self.surface())
        foreground = self.theme.on_surface(self.surface())
        self.configure(ttk_style, background=background, foreground=foreground)
        self.map(ttk_style, background=[])
