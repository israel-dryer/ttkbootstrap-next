from ttkbootstrap.style import Element, ElementImage, StyleManager
from ttkbootstrap.style.utils import recolor_image


class BadgeStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        super().__init__("Badge.TLabel", **kwargs)
        self.options.set_defaults(color='primary', variant='default', select_background='primary')


@BadgeStyleBuilder.register_variant('default')
@BadgeStyleBuilder.register_variant('pill')
@BadgeStyleBuilder.register_variant('circle')
def build_default_badge_style(b: BadgeStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    surface_token = b.options('surface')
    color_token = b.options('color')
    variant = b.options('variant')

    surface = b.color(surface_token)
    normal = b.color(color_token)
    foreground = b.on_color(normal)

    # button element images
    normal_img = recolor_image(f'badge-{variant}', normal)

    border = 8
    padding = (8, 0)
    if variant == 'circle':
        padding = 3
        border = 8

    # button element
    b.style_create_element(
        ElementImage(
            f'{ttk_style}.border', normal_img,
            sticky="nsew", border=border, padding=padding))

    b.style_create_layout(
        ttk_style, Element(f"{ttk_style}.border", sticky="").children(
            [
                Element("Label.padding", sticky="nsew").children(
                    [
                        Element("Label.label", sticky="")
                    ])
            ]))

    b.style_configure(ttk_style, background=surface, foreground=foreground, padding=0)


@BadgeStyleBuilder.register_variant('list')
def build_list_badge_style(b: BadgeStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    surface_token = b.options('surface')

    surface = b.color(surface_token)
    normal = b.color(b.options('color'))
    selected = b.active(normal)
    foreground = b.on_color(normal)
    background_hover = b.elevate(surface, 1)
    background_selected = b.color(b.options('select_background'))
    background_selected_hover = b.hover(background_selected)

    # button element images
    normal_img = recolor_image('badge-circle', normal)
    selected_img = recolor_image('badge-circle', selected)

    border = 8
    padding = 3

    # button element
    b.style_create_element(
        ElementImage(
            f'{ttk_style}.border', normal_img,
            sticky="nsew", border=border, padding=padding).state_specs(
            [
                ('selected', selected_img)]))

    b.style_create_layout(
        ttk_style, Element(f"{ttk_style}.border", sticky="").children(
            [
                Element("Label.padding", sticky="nsew").children(
                    [
                        Element("Label.label", sticky="")
                    ])
            ]))

    b.style_configure(ttk_style, background=surface, foreground=foreground, padding=0)
    b.style_map(
        ttk_style,
        background=[
            ('selected hover', background_selected_hover),
            ('selected', background_selected),
            ('hover', background_hover)])
