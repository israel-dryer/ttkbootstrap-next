from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import Element, ElementImage
from ttkbootstrap.style.utils import recolor_image


class FrameStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__("TFrame", **kwargs)
        self.options.setdefault('select_background', 'primary')

    def register_style(self):
        variant = self.options.get('variant')
        if variant == 'field':
            self.build_field_style()
        elif variant == 'list':
            self.build_list_style()
        else:
            self.build_default_style()

    def build_default_style(self):
        ttk_style = self.resolve_name()
        background = self.theme.color(self.surface())
        self.configure(ttk_style, background=background)

    def build_list_style(self):
        ttk_style = self.resolve_name()
        background = self.theme.color(self.surface())
        background_hover = self.theme.elevate(background, 1)
        background_pressed = self.theme.elevate(background, 2)
        background_selected = self.theme.color(self.options.get("select_background"), background)
        background_selected_hover = self.theme.hover(background_selected)
        self.configure(ttk_style, background=background)
        self.map(
            ttk_style,
            background=[
                ('selected hover', background_selected_hover),
                ('selected', background_selected),
                ('pressed', background_pressed),
                ('hover', background_hover)
            ])

    def build_field_style(self):

        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        color_token = self.options.get("select_background")

        surface = theme.color(surface_token)
        color = theme.color(color_token)
        normal = surface
        border = theme.border(surface)
        disabled = theme.disabled('text')
        focused_border = theme.focus_border(color)
        focused_ring = theme.focus_ring(color, surface)

        # input element images
        normal_img = recolor_image(f'input', normal, border, surface)
        focused_img = recolor_image(f'input', normal, focused_border, focused_ring)
        disabled_img = recolor_image(f'input', normal, disabled, surface, surface)

        # input element
        self.create_element(
            ElementImage(f'{ttk_style}.border', normal_img, sticky="nsew", border=8).state_specs(
                [
                    ('disabled', disabled_img),
                    ('focus', focused_img),
                ]
            )
        )
        self.style_layout(
            ttk_style, Element(f'{ttk_style}.border', sticky="nsew").children(
                [
                    Element(f'{ttk_style}.padding', sticky="")
                ]))
        self.configure(ttk_style, background=surface)
