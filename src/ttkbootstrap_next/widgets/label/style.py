from tkinter import TclError
from tkinter.font import nametofont
from typing import override

from ttkbootstrap_next.style import StyleManager

_images = []


class LabelStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        super().__init__("TLabel", **kwargs)
        self.options.set_defaults(variant="default", select_background="primary")

    @override
    def icon_font_size(self) -> int:
        """Return the icon size scaled from font size."""
        factor = 0.9
        fnt = nametofont('body-lg')
        font_size = fnt.metrics('linespace')
        return int(font_size * factor)


@LabelStyleBuilder.register_variant("default")
def build_default_label_style(b: LabelStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()
    foreground_token = b.options("foreground")
    background_token = b.options("background")

    if background_token is None:
        background = b.color(b.surface_token)
    else:
        background = b.color(background_token)

    if foreground_token is None:
        foreground = b.on_color(background)
    else:
        try:
            foreground = b.color(foreground_token, "text")
        except TclError:
            foreground = b.options('foreground')
    b.style_configure(ttk_style, background=background, foreground=foreground)
