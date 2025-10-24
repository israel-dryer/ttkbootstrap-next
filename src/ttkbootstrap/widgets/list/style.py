# Composite styles for the list widgets
from tkinter import TclError

from ttkbootstrap.layouts.style import FrameStyleBuilder
from ttkbootstrap.style import Element, ElementImage
from ttkbootstrap.style.utils import recolor_image
from ttkbootstrap.widgets.button.style import ButtonStyleBuilder
from ttkbootstrap.widgets.label.style import LabelStyleBuilder


@FrameStyleBuilder.register_variant("list")
def build_list_frame_style(b: FrameStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    background = b.color(b.surface_token)
    background_hover = b.elevate(background, 1)
    background_pressed = b.elevate(background, 2)
    background_selected = b.color(b.options("select_background"), background)
    background_selected_hover = b.hover(background_selected)
    b.style_configure(ttk_style, background=background)
    b.style_map(
        ttk_style,
        background=[
            ('focus selected', background_selected_hover),
            ('selected hover', background_selected_hover),
            ('selected', background_selected),
            ('pressed', background_pressed),
            ('hover', background_hover),
            ('focus', background_hover),
            ((), background)
        ])


@FrameStyleBuilder.register_variant("list-item")
@FrameStyleBuilder.register_variant("list-item-separated")
def build_list_item_style(b: FrameStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    background = b.color(b.surface_token)
    background_hover = b.elevate(background, 1)
    background_pressed = b.elevate(background, 2)
    background_selected = b.color(b.options("select_background"), background)
    background_selected_hover = b.hover(background_selected)
    border_normal = b.border(background) if b.variant.endswith('separated') else background
    focus_color = b.elevate(background_selected, 5)
    if b.options("focus_color"):
        focus_color = b.color(b.options("focus_color"))

    normal_img = recolor_image('list-item-separated', background, border_normal)
    hover_img = recolor_image('list-item-separated', background_hover, border_normal)
    selected_img = recolor_image('list-item-separated', background_selected, border_normal)
    selected_hover_img = recolor_image('list-item-separated', background_selected_hover, border_normal)
    pressed_img = recolor_image('list-item-separated', background_pressed, border_normal)

    focus_img = recolor_image('list-item-focus', background_hover, border_normal, focus_color)
    focus_pressed_img = recolor_image('list-item-focus', background_pressed, border_normal, focus_color)
    focus_hover_img = recolor_image('list-item-focus', background_hover, border_normal, focus_color)
    focus_selected_img = recolor_image('list-item-focus', background_selected_hover, border_normal, focus_color)
    focus_selected_hover_img = recolor_image('list-item-focus', background_selected_hover, border_normal, focus_color)

    # list element
    b.style_create_element(
        ElementImage(f'{ttk_style}.border', normal_img, sticky="nsew", border=8).state_specs(
            [
                # Most specific combos (first match wins)
                ('focus selected hover', focus_selected_hover_img),
                ('focus selected', focus_selected_img),
                ('hover selected', selected_hover_img),
                ('focus pressed', focus_pressed_img),
                ('focus hover', focus_hover_img),
                ('selected', selected_img),
                ('pressed', pressed_img),
                ('hover', hover_img),
                ('focus', focus_img),
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


@ButtonStyleBuilder.register_variant("list")
def build_list_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    background_hover = b.elevate(surface, 1)
    background_pressed = b.elevate(surface, 2)
    background_selected = b.color(b.options('select_background'))
    background_selected_hover = b.hover(background_selected)

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
            ('focus selected', background_selected_hover),
            ('selected hover', background_selected_hover),
            ('selected', background_selected),
            ('pressed', background_pressed),
            ('hover', background_hover),
            ('focus', background_hover)])


@ButtonStyleBuilder.register_variant("list-icon-builder")
def build_list_icon_assets(b: ButtonStyleBuilder, icon: dict):
    """Create stateful icons for list variant"""
    icon['size'] = 14
    background = b.color(b.surface_token)
    background_selected = b.color(b.options('select_background'))
    foreground = b.on_color(background)
    foreground_selected = b.on_color(background_selected)
    foreground_disabled = b.disabled("text")

    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'focus', foreground)
    b.register_stateful_icon(icon, 'selected', foreground_selected)
    b.map_stateful_icons()


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
