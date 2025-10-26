from tkinter import TclError

from ttkbootstrap_next.layouts.style import FrameStyleBuilder
from ttkbootstrap_next.style.element import Element, ElementImage
from ttkbootstrap_next.style.utils import recolor_image
from ttkbootstrap_next.widgets.button.style import ButtonStyleBuilder, button_img_border, create_button_style
from ttkbootstrap_next.widgets.label.style import LabelStyleBuilder


@FrameStyleBuilder.register_variant("field")
def build_field_frame_style(b: FrameStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    color_token = b.options("select_background")

    surface = b.color(b.surface_token)
    color = b.color(color_token)
    normal = surface
    border = b.border(surface)
    disabled = b.disabled('text')
    focused_border = b.focus_border(color)
    focused_ring = b.focus_ring(color, surface)

    # input element images
    normal_img = recolor_image(f'input', normal, border, surface)
    focused_img = recolor_image(f'input', normal, focused_border, focused_ring)
    disabled_img = recolor_image(f'input', normal, disabled, surface, surface)

    # input element
    b.style_create_element(
        ElementImage(f'{ttk_style}.border', normal_img, sticky="nsew", border=8).state_specs(
            [
                ('disabled', disabled_img),
                ('focus', focused_img),
            ]
        )
    )
    b.style_create_layout(
        ttk_style, Element(f'{ttk_style}.border', sticky="nsew").children(
            [
                Element(f'{ttk_style}.padding', sticky="")
            ]))
    b.style_configure(ttk_style, background=surface)


@ButtonStyleBuilder.register_variant("prefix-icon-builder")
@ButtonStyleBuilder.register_variant("suffix-icon-builder")
def build_addon_icon_assets(b: ButtonStyleBuilder, icon: dict):
    """Create stateful icons for addon variant"""
    surface = b.color(b.surface_token)
    foreground = b.on_color(surface)
    foreground_disabled = b.disabled("text")
    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'focus', foreground)
    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.map_stateful_icons()


@ButtonStyleBuilder.register_variant("prefix")
@ButtonStyleBuilder.register_variant("suffix")
def build_addon_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    border = b.border(surface)
    foreground = b.on_color(surface)
    foreground_disabled = b.disabled("text")
    normal = b.disabled()
    pressed = b.subtle('secondary', surface)
    focused = hovered = pressed

    # button element images
    normal_img = recolor_image(f'input-{b.variant}', normal, border)
    pressed_img = recolor_image(f'input-{b.variant}', pressed, border, surface, surface)
    hovered_img = recolor_image(f'input-{b.variant}', hovered, border, surface, surface)
    focused_img = recolor_image(f'input-{b.variant}', focused, border, focused, surface)
    focused_hovered_img = recolor_image(f'input-{b.variant}', hovered, border, focused, surface)
    focused_pressed_img = recolor_image(f'input-{b.variant}', pressed, border, focused, surface)
    disabled_img = recolor_image(f'input-{b.variant}', normal, border, surface, surface)
    btn_padding = button_img_border(b.options("size"))

    # button element
    b.style_create_element(
        ElementImage(
            f'{ttk_style}.border', normal_img, sticky="nsew", border=btn_padding,
            padding=btn_padding).state_specs(
            [
                ('disabled', disabled_img),
                ('focus pressed', focused_pressed_img),
                ('focus hover', focused_hovered_img),
                ('focus', focused_img),
                ('pressed', pressed_img),
                ('hover', hovered_img),
            ]))

    create_button_style(b)
    b.style_configure(
        ttk_style,
        background=surface,
        foreground=foreground,
        relief='flat',
        stipple="gray12",
        padding=0,
        font=b.get_font(b.options('size')))

    b.style_map(
        ttk_style,
        foreground=[('disabled', foreground_disabled)],
        background=[('disabled', surface)])


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
