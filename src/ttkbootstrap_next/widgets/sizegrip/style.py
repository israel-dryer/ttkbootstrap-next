from ttkbootstrap_next.style import StyleManager


class SizegripStyleBuilder(StyleManager):
    def __init__(self, **kwargs):
        super().__init__("TSizegrip", **kwargs)
        self.options.set_defaults(variant="default")


@SizegripStyleBuilder.register_variant("default")
def build_default_sizegrip_style(b: SizegripStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    background = b.color(b.surface_token)
    if b.color_token is None:
        foreground = b.on_color(background)
    else:
        foreground = b.color(b.color_token)
    b.style_configure(ttk_style, background=background, foreground=foreground)
    # TODO update with custom image layout and style
