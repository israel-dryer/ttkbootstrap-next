from ttkbootstrap.style import (Element, ElementImage, StyleManager)
from ttkbootstrap.style.utils import recolor_image


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

    normal_img = recolor_image('list-item-separated', background, border_normal)
    hover_img = recolor_image('list-item-separated', background_hover, border_normal)
    selected_img = recolor_image('list-item-separated', background_selected, border_normal)
    selected_hover_img = recolor_image('list-item-separated', background_selected_hover, border_normal)
    pressed_img = recolor_image('list-item-separated', background_pressed, border_normal)

    focus_img = recolor_image('list-item-separated', background_hover, border_normal)
    focus_hover_img = recolor_image('list-item-separated', background_hover, border_normal)
    focus_selected_img = recolor_image('list-item-separated', background_selected_hover, border_normal)
    focus_selected_hover_img = recolor_image('list-item-separated', background_selected_hover, border_normal)

    # list element
    b.style_create_element(
        ElementImage(f'{ttk_style}.border', normal_img, sticky="nsew", border=8).state_specs(
            [
                # Most specific combos (first match wins)
                ('focus selected', focus_selected_hover_img),
                ('hover selected', selected_hover_img),
                ('focus selected', focus_selected_img),
                ('selected', selected_img),
                ('focus pressed', pressed_img),
                ('pressed', pressed_img),
                ('focus hover', focus_hover_img),
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
