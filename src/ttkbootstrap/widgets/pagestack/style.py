from ttkbootstrap.style import StyleManager


class PageStackStyleBuilder(StyleManager):
    def __init__(self, **kwargs):
        super().__init__("TNotebook", **kwargs)
        self.options.set_defaults(variant="default")


@PageStackStyleBuilder.register_variant("default")
def build_default_page_stack_style(b: PageStackStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    background = b.color(b.surface_token)
    b.style_configure(
        ttk_style,
        bordercolor=background,  # remove border
        lightcolor=background,  # remove border
        darkcolor=background,  # remove border
        background=background,
    )
    # remove the tabs by creating an empty layout
    b.style.ttk.layout(f'{ttk_style}.Tab', [])
