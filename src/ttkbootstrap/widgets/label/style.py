from tkinter import TclError
from tkinter.font import nametofont
from typing import override

from ttkbootstrap.style import Element, ElementImage, StyleManager, recolor_image

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


@LabelStyleBuilder.register_variant("prefix")
@LabelStyleBuilder.register_variant("suffix")
def build_addon_label_style(b: LabelStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()
    surface = b.color(b.surface_token)
    border = b.border(surface)
    foreground = b.on_color(surface)
    normal = b.disabled()

    # button element images
    normal_img = recolor_image(f'input-{b.variant}', normal, border)
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
@LabelStyleBuilder.register_variant("list-radio")
@LabelStyleBuilder.register_variant("list-checkbox")
def build_list_label_style(b: LabelStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()
    background = b.color(b.surface_token)
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
            ('focus selected', background_selected_hover),
            ('selected hover', background_selected_hover),
            ('selected', background_selected),
            ('pressed', background_pressed),
            ('hover', background_hover),
            ('focus', background_hover)],
        foreground=[('selected', foreground_selected)]
    )


@LabelStyleBuilder.register_variant("menu-item")
def build_menu_item_label_style(b: LabelStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()
    background = b.color(b.surface_token)
    background_hover = b.elevate(background, 1)
    background_pressed = b.elevate(background, 2)
    foreground_token = b.options('foreground')
    if foreground_token is None:
        foreground = b.on_color(background)
    else:
        try:
            foreground = b.color(foreground_token, "text")
        except TclError:
            foreground = foreground_token

    b.style_configure(ttk_style, background=background, foreground=foreground)
    b.style_map(
        ttk_style,
        background=[
            ('pressed', background_pressed),
            ('hover', background_hover)]
    )


# ----- Icon builders ------

@LabelStyleBuilder.register_variant("prefix-icon-builder")
@LabelStyleBuilder.register_variant("suffix-icon-builder")
@LabelStyleBuilder.register_variant("default-icon-builder")
def build_default_icon_assets(b: LabelStyleBuilder, icon: dict):
    background = b.color(b.surface_token)
    foreground_token = b.options('foreground')
    if foreground_token is None:
        foreground = b.on_color(background)
    else:
        try:
            foreground = b.color(foreground_token, "text")
        except TclError:
            foreground = foreground_token

    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'focus', foreground)
    b.register_stateful_icon(icon, 'disabled', foreground)
    b.map_stateful_icons()


@LabelStyleBuilder.register_variant("menu-item-icon-builder")
def build_menu_item_icon_assets(b: LabelStyleBuilder, icon: dict):
    icon['size'] = 14
    background = b.color(b.surface_token)
    foreground_token = b.options('foreground')
    if foreground_token is None:
        foreground = b.on_color(background)
    else:
        try:
            foreground = b.color(foreground_token, "text")
        except TclError:
            foreground = foreground_token

    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'disabled', foreground)
    b.register_stateful_icon(icon, 'selected', foreground)
    b.map_stateful_icons()


@LabelStyleBuilder.register_variant("list-icon-builder")
def build_list_icon_assets(b: LabelStyleBuilder, icon: dict):
    icon['size'] = 14
    background = b.color(b.surface_token)
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

    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'focus', foreground)
    b.register_stateful_icon(icon, 'disabled', foreground)
    b.register_stateful_icon(icon, 'selected', foreground_selected)
    b.map_stateful_icons()
