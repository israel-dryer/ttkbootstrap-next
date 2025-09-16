from ttkbootstrap.style import StyleBuilderBase


class NotebookStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__("TNotebook", **kwargs)

    def register_style(self):
        self.build_default_style()

    def build_default_style(self):
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
