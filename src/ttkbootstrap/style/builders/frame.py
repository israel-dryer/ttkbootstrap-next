from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import Element, ElementImage
from ttkbootstrap.style.utils import recolor_image


class FrameStyleBuilder(StyleBuilderBase):

    def __init__(self, variant: str = None, **kwargs):
        super().__init__("TFrame", variant=variant, **kwargs)

    def variant(self, value: str = None):
        if value is None:
            return self.options.get('variant', None)
        else:
            self.options.update(variant=value)
            return self

    def color(self, value: str = None):
        if value is None:
            return self.options.get('color') or 'primary'
        else:
            self.options.update(color=value)
            return self

    def size(self, value: str = None):
        if value is None:
            return self.options.get('size') or 'md'
        else:
            self.options.update(size=value)
            return self

    def surface(self, value: str = None):
        if value is None:
            return self._surface
        else:
            self._surface = value
            return self

    def register_style(self):
        if self.variant() == 'field':
            self.field()
        else:
            self.default()

    def default(self):
        ttk_style = self.resolve_name()
        background = self.theme.color(self.surface())
        self.configure(ttk_style, background=background)

    def field(self):

        def img_border(size):
            if size == "sm":
                return 6
            elif size == "md":
                return 8
            else:
                return 10

        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        color_token = self.color()

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
            ElementImage(f'{ttk_style}.border',normal_img, sticky="nsew", border=8).state_specs(
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
