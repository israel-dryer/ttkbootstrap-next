# Composite styles for the menu widgets
from tkinter import Menu, TclError

from ttkbootstrap_next.layouts.style import FrameStyleBuilder
from ttkbootstrap_next.style import Element, StyleManager
from ttkbootstrap_next.style.element import ElementImage
from ttkbootstrap_next.style.utils import recolor_image
from ttkbootstrap_next.widgets.button.style import ButtonStyleBuilder
from ttkbootstrap_next.widgets.label.style import LabelStyleBuilder


class MenuStyleBuilder(StyleManager):

    def __init__(self, menu: Menu, **kwargs):
        super().__init__("tkinter", **kwargs)
        self._window: Menu = menu
        self.options.set_defaults(surface="background", variant="default")

    @property
    def window(self):
        return self._window


@MenuStyleBuilder.register_variant("default")
def build_default_window_style(b: MenuStyleBuilder):
    background = b.color(b.surface_token or "background")
    foreground= b.on_color(background)
    b.window.configure(background=background, foreground=foreground)


@FrameStyleBuilder.register_variant("menu-item")
def build_menu_item_style(b: FrameStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    background = b.color(b.surface_token)
    background_hover = b.elevate(background, 1)
    background_pressed = b.elevate(background, 2)
    begin_group = b.options('begin_group') or False
    border_normal = b.border(background) if begin_group else background

    normal_img = recolor_image('menu-item-separated', background, border_normal)
    hover_img = recolor_image('menu-item-separated', background_hover, border_normal)
    pressed_img = recolor_image('menu-item-separated', background_pressed, border_normal)

    # menu item element
    b.style_create_element(
        ElementImage(f'{ttk_style}.border', normal_img, sticky="nsew", border=8).state_specs(
            [
                # Most specific combos (first match wins)
                ('pressed', pressed_img),
                ('hover', hover_img),
                ((), normal_img),
            ]
        )
    )
    b.style_create_layout(
        ttk_style, Element(f'{ttk_style}.border', sticky="nsew").children(
            [
                Element(f'{ttk_style}.padding', sticky="")
            ])
    )
    b.style_configure(ttk_style, background=background)


@ButtonStyleBuilder.register_variant("menu-item")
def build_menu_item_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    background_hover = b.elevate(surface, 1)
    background_pressed = b.elevate(surface, 2)

    # button element
    b.style_create_layout(
        ttk_style, Element('Label.border', sticky="nsew").children(
            [
                Element('Label.padding', sticky="nsew").children(
                    [
                        Element("Label.label", sticky="")
                    ])
            ]))

    b.style_configure(
        ttk_style,
        background=surface,
        padding=0,
        relief='flat',
        stipple="gray12",
        font=b.get_font(b.options('size')))

    b.style_map(
        ttk_style,
        foreground=[],
        background=[
            ('pressed', background_pressed),
            ('hover', background_hover)])


@ButtonStyleBuilder.register_variant("menu-item-icon-builder")
def build_menu_icon_assets(b: ButtonStyleBuilder, icon: dict):
    """Create stateful icons for menu item variant"""
    icon['size'] = 14
    background = b.color(b.surface_token)
    foreground = b.on_color(background)
    foreground_disabled = b.disabled("text")

    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'selected', foreground)
    b.map_stateful_icons()


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
