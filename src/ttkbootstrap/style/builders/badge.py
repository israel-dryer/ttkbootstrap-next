from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import ElementImage, Element
from ttkbootstrap.style.utils import recolor_image


class BadgeStyleBuilder(StyleBuilderBase):

    def __init__(self, color="primary", variant="default", **kwargs):
        super().__init__("Badge.TLabel", color=color, variant=variant, **kwargs)

    def select_background(self, value: str = None):
        if value is None:
            return self.options.get('select_background') or 'primary'
        else:
            self.options.update(select_background=value)
            return self

    def color(self, value: str = None):
        if value is None:
            return self.options.get('color') or 'primary'
        else:
            self.options.update(color=value)
            return self

    def variant(self, value: str = None):
        if value is None:
            return self.options.get('variant') or 'default'
        else:
            self.options.update(variant=value)
            return self

    def register_style(self):
        if self.variant() == 'list':
            self.build_list_style()
        else:
            self.build_default_style()

    def build_default_style(self):
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()

        surface = theme.color(surface_token)
        normal = self.theme.color(self.color())
        foreground = theme.on_color(normal)

        # button element images
        normal_img = recolor_image(f'badge-{self.variant()}', normal)

        border = 8
        padding = (8, 0)
        if self.variant() == 'circle':
            padding = 3
            border = 8

        # button element
        self.create_element(
            ElementImage(
                f'{ttk_style}.border', normal_img,
                sticky="nsew", border=border, padding=padding))

        ttk_style = self.resolve_name()
        self.style_layout(
            ttk_style, Element(f"{ttk_style}.border", sticky="").children(
                [
                    Element("Label.padding", sticky="nsew").children(
                        [
                            Element("Label.label", sticky="")
                        ])
                ]))

        self.configure(ttk_style, background=surface, foreground=foreground, padding=0)

    def build_list_style(self):
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()

        surface = theme.color(surface_token)
        normal = self.theme.color(self.color())
        selected = self.theme.active(normal)
        foreground = theme.on_color(normal)
        background_hover = theme.elevate(surface, 1)
        background_selected = theme.color(self.select_background())
        background_selected_hover = theme.hover(background_selected)

        # button element images
        normal_img = recolor_image('badge-circle', normal)
        selected_img = recolor_image('badge-circle', selected)

        border = 8
        padding = 3

        # button element
        self.create_element(
            ElementImage(
                f'{ttk_style}.border', normal_img,
                sticky="nsew", border=border, padding=padding).state_specs(
                [
                    ('selected', selected_img)]))

        ttk_style = self.resolve_name()
        self.style_layout(
            ttk_style, Element(f"{ttk_style}.border", sticky="").children(
                [
                    Element("Label.padding", sticky="nsew").children(
                        [
                            Element("Label.label", sticky="")
                        ])
                ]))

        self.configure(ttk_style, background=surface, foreground=foreground, padding=0)
        self.map(
            ttk_style,
            background=[
                ('selected hover', background_selected_hover),
                ('selected', background_selected),
                ('hover', background_hover)])
