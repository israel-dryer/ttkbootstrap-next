from ttkbootstrap.style.builders.base import StyleBuilderBase


class NotebookStyleBuilder(StyleBuilderBase):

    def __init__(self):
        super().__init__("TNotebook")

    def surface(self, value: str = None):
        if value is None:
            return self._surface
        else:
            self._surface = value
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        surface_token = self.surface()

        background = self.theme.color(surface_token)
        foreground = self.theme.on_color(background)
        border = self.theme.border(background)
        self.configure(
            ttk_style,
            background=background,
            bordercolor=border,
            lightcolor=background,
            darkcolor=background
        )

        self.configure(
            f"{ttk_style}.Tab",
            background=background,
            foreground=foreground,
            bordercolor=border,
            lightcolor=background,
            darkcolor=background,
            focuscolor='')

        self.map(
            f"{ttk_style}.Tab",
            foreground=[], background=[],
            bordercolor=[('!selected', background)],
            darkcolor=[], lightcolor=[])
