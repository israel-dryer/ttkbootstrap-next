from tkinter import TclError
from tkinter.font import nametofont

from ttkbootstrap.icons import BootstrapIcon
from ttkbootstrap.style import Element, ElementImage, StyleManager, recolor_image

_images = []


class LabelStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        super().__init__("TLabel", **kwargs)
        self.options.set_defaults(variant="default", select_background="primary")
        self._stateful_icons: dict[str, BootstrapIcon] = dict()

    @property
    def stateful_icons(self):
        return self._stateful_icons

    def register_style(self):
        self.build()


@LabelStyleBuilder.register_variant("default")
def build_default_label_style(b: LabelStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    surface_token = b.surface_token()
    foreground_token = b.options("foreground")
    background_token = b.options("background")

    if background_token is None:
        background = b.color(surface_token)
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


@LabelStyleBuilder.register_variant("addon")
def build_addon_label_style(b: LabelStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    surface_token = b.surface_token()

    surface = b.color(surface_token)
    border = b.border(surface)
    foreground = b.on_color(surface)
    normal = b.disabled()

    # button element images
    normal_img = recolor_image(f'input-{b.options('variant')}', normal, border)
    img_padding = 8

    # button element
    b.style_create_element(
        ElementImage(
            f'{ttk_style}.border', normal_img, sticky="nsew", border=img_padding, padding=img_padding))

    b.style_create_layout(
        ttk_style, Element(f"{ttk_style}.border", sticky="nsew").children(
            [
                Element("Label.padding", sticky="nsew").children(
                    [
                        Element("Label.label", sticky="")
                    ])
            ]))

    b.style_configure(
        ttk_style,
        background=surface,
        foreground=foreground,
        relief='flat',
        stipple="gray12",
        padding=0
    )


@LabelStyleBuilder.register_variant("list")
def build_list_label_style(b: LabelStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    background = b.color(b.surface_token())
    background_hover = b.elevate(background, 1)
    background_pressed = b.elevate(background, 2)
    background_selected = b.color(b.options('select_background'))
    background_selected_hover = b.hover(background_selected)
    foreground_token = b.options('foreground')
    if foreground_token is None:
        foreground = b.on_color(background)
    else:
        try:
            foreground = b.color(foreground_token, "text")
        except TclError:
            foreground = foreground_token

    foreground_selected = b.on_color(background_selected)
    b.style_configure(ttk_style, background=background, foreground=foreground)
    b.style_map(
        ttk_style,
        background=[
            ('selected hover', background_selected_hover),
            ('selected', background_selected),
            ('pressed', background_pressed),
            ('hover', background_hover)],
        foreground=[('selected', foreground_selected)]
    )


def build_icon_assets(b: LabelStyleBuilder, icon: dict):
    if icon is None: return
    if b.options('variant') == 'list':
        build_list_icon_assets(b, icon)
    else:
        build_default_icon_assets(b, icon)


def build_default_icon_assets(b: LabelStyleBuilder, icon: dict):
    background = b.color(b.surface_token())
    foreground_token = b.options('foreground')
    if foreground_token is None:
        foreground = b.on_color(background)
    else:
        try:
            foreground = b.color(foreground_token, "text")
        except TclError:
            foreground = foreground_token

    create_icon_asset(b, icon, 'normal', foreground)
    create_icon_asset(b, icon, 'hover', foreground)
    create_icon_asset(b, icon, 'pressed', foreground)
    create_icon_asset(b, icon, 'focus', foreground)
    create_icon_asset(b, icon, 'disabled', foreground)


def create_icon_asset(b: LabelStyleBuilder, icon: dict, state: str, color: str):
    # create stateful icons to be mapped by the buttons event handling logic
    options = dict(icon)
    options.setdefault('size', icon_font_size())
    options.setdefault('color', color)
    b.stateful_icons[state] = BootstrapIcon(**options)


def build_list_icon_assets(b: LabelStyleBuilder, icon: dict):
    icon['size'] = 14
    background = b.color(b.surface_token())
    foreground_token = b.options('foreground')
    if foreground_token is None:
        foreground = b.on_color(background)
    else:
        try:
            foreground = b.color(foreground_token, "text")
        except TclError:
            foreground = foreground_token

    background_selected = b.color(b.options('select_background'))
    foreground_selected = b.on_color(background_selected)

    create_icon_asset(b, icon, 'normal', foreground)
    create_icon_asset(b, icon, 'hover', foreground)
    create_icon_asset(b, icon, 'pressed', foreground)
    create_icon_asset(b, icon, 'focus', foreground)
    create_icon_asset(b, icon, 'disabled', foreground)
    create_icon_asset(b, icon, 'selected', foreground_selected)


def icon_font_size() -> int:
    """Return the icon size scaled from font size."""
    factor = 0.9
    fnt = nametofont('body-lg')
    font_size = fnt.metrics('linespace')
    return int(font_size * factor)
