from ttkbootstrap.style import (StyleManager)


class FrameStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        super().__init__("TFrame", **kwargs)
        self.options.set_defaults(select_background="primary", variant="default")


@FrameStyleBuilder.register_variant("default")
def build_default_frame_style(b: FrameStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    border_token = b.options('border')
    background = b.color(b.surface_token)

    if border_token is True:
        border_color = b.border(background)
    elif border_token in (False, None):
        border_color = background
    else:
        border_color = b.color(border_token)

    b.style_configure(
        ttk_style,
        background=background,
        relief='raised',
        bordercolor=border_color,
        darkcolor=background,
        lightcolor=background,
    )
