from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import Element


class NotebookStyleBuilder(StyleBuilderBase):

    def __init__(self, variant=None, **kwargs):
        self._variant = variant
        super().__init__("TNotebook", **kwargs)

    def surface(self, value: str = None):
        if value is None:
            return self._surface
        else:
            self._surface = value
            return self

    def variant(self, value: str = None):
        if value is None:
            return self._variant
        else:
            self._variant = value
            return self

    def register_style(self):
        if self.variant() == 'pages':
            self.build_pages_style()
        else:
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

    def build_pages_style(self):
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        background = self.theme.color(surface_token)
        self.configure(
            ttk_style,
            bordercolor=background,     # remove border
            lightcolor=background,      # remove border
            darkcolor=background,       # remove border
            background=background,
        )
        # remove the tabs by creating an empty layout
        self.style.ttk.layout(f'{ttk_style}.Tab', [])
