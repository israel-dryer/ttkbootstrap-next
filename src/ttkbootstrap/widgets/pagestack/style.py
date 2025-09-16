from ttkbootstrap.style.builders.base import StyleBuilderBase


class PageStackStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__("TNotebook", **kwargs)

    def register_style(self):
        self.build_default_style()

    def build_default_style(self):
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        background = self.theme.color(surface_token)
        self.configure(
            ttk_style,
            bordercolor=background,  # remove border
            lightcolor=background,  # remove border
            darkcolor=background,  # remove border
            background=background,
        )
        # remove the tabs by creating an empty layout
        self.style.ttk.layout(f'{ttk_style}.Tab', [])
