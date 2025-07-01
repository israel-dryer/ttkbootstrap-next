from .base import StyleBuilderBase
from ..element import Element, ElementImage
from ..utils import recolor_image
from ...core.image import ManagedImage

_images = []


class ButtonStyleBuilder(StyleBuilderBase):

    def __init__(
            self, color: str = "primary", variant: str = "solid", surface: str = None, size: str = "md",
            icon: str = None):
        super().__init__(
            "TButton",
            surface=surface,
            color=color,
            variant=variant,
            size=size,
            icon=icon
        )

    def color(self, value: str = None):
        if value is None:
            return self.options.get('color', 'primary')
        else:
            self.options.update(color=value)
            return self

    def variant(self, value: str = None):
        if value is None:
            return self.options.get('variant', 'solid')
        else:
            self.options.update(variant=value)
            return self

    def size(self, value: str = None):
        if value is None:
            return self.options.get('size', 'md')
        else:
            self.options.update(size=value)
            return self

    def icon(self, value: str = None):
        if value is None:
            return self.options.get('icon', None)
        else:
            self.options.update(icon=value)
            return self

    def register_style(self):
        if self.variant() == 'solid':
            self.solid_button()
        elif self.variant() == 'outline':
            self.outline_button()
        elif self.variant() == 'link':
            self.link_button()

    def solid_button(self):
        ttk_style = self.resolve_name()
        foreground = self.theme.on_color(self.color())
        foreground_disabled = self.theme.on_surface_disabled()
        normal = self.theme.color(self.color())
        pressed = self.theme.pressed(self.color())
        hovered = self.theme.hovered(self.color())
        focused = hovered
        focused_ring = self.theme.focused_ring(self.color())
        focused_border = self.theme.focused_border(self.color())
        disabled = self.theme.disabled(self.color())
        surface = self.theme.surface_color(self.surface())

        normal_img = recolor_image(f'btn-{self.size()}', normal, normal, surface)
        pressed_img = recolor_image(f'btn-{self.size()}', pressed, pressed, surface)
        hovered_img = recolor_image(f'btn-{self.size()}', hovered, hovered, surface)
        focused_img = recolor_image(f'btn-{self.size()}', focused, focused_border, focused_ring)
        focused_hovered_img = recolor_image(f'btn-{self.size()}', hovered, focused_border, focused_ring)
        focused_pressed_img = recolor_image(f'btn-{self.size()}', pressed, focused_border, focused_ring)
        disabled_img = recolor_image(f'btn-{self.size()}', disabled, disabled, surface)

        self.create_element(
            ElementImage(f'{ttk_style}.border', normal_img, sticky="nsew", border=4, padding=6).state_specs(
                [
                    ('disabled', disabled_img),
                    ('focus pressed', focused_pressed_img),
                    ('focus hover', focused_hovered_img),
                    ('focus', focused_img),
                    ('pressed', pressed_img),
                    ('hover', hovered_img),
                ]))

        self.style_layout(ttk_style, Element(f"{ttk_style}.border", sticky="nsew").children([
            Element("Button.padding", sticky="nsew").children([
                Element("Button.label", sticky="nsew", expand=1)
            ])
        ]))

        self.configure(ttk_style, background=surface, foreground=foreground)
        self.map(ttk_style, foreground=[('disabled', foreground_disabled)], background=[])

    def outline_button(self):
        pass

    def link_button(self):
        pass


def label_sticky(size: str):
    """Calculate label sticky based on button size"""
    return "w" if size in ['sm', 'md'] else "nw"


def icon_sticky(size: str):
    """Calculate icon sticky based on button size"""
    return "e" if size in ['sm', 'md'] else "ne"


def button_padding(size: str) -> tuple[int, int]:
    """Calculate button padding based on button size"""
    if size == "sm":
        return 12, 4
    else:
        return 12, 12
