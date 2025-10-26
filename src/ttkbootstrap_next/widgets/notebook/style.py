from ttkbootstrap_next.style import StyleManager


class NotebookStyleBuilder(StyleManager):
    def __init__(self, **kwargs):
        super().__init__("TNotebook", **kwargs)
        self.options.set_defaults(variant="default")


@NotebookStyleBuilder.register_variant("default")
def build_default_notebook_style(b: NotebookStyleBuilder):
    ttk_style = b.resolve_ttk_name()

    background = b.color(b.surface_token)
    foreground = b.on_color(background)
    border = b.border(background)
    b.style_configure(
        ttk_style,
        background=background,
        bordercolor=border,
        lightcolor=background,
        darkcolor=background
    )

    b.style_configure(
        f"{ttk_style}.Tab",
        background=background,
        foreground=foreground,
        bordercolor=border,
        lightcolor=background,
        darkcolor=background,
        focuscolor='')

    b.style_map(
        f"{ttk_style}.Tab",
        foreground=[], background=[],
        bordercolor=[('!selected', background)],
        darkcolor=[], lightcolor=[])


@NotebookStyleBuilder.register_variant("buttons")
def build_button_tab_notebook_style(b: NotebookStyleBuilder):
    # TODO implement bootstrap button style notebook
    pass
