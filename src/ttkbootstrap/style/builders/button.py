from tkinter.font import nametofont

from .base import StyleBuilderBase
from ..element import Element, ElementImage
from ..utils import recolor_image
from ...icons import BootstrapIcon

_images = []


class ButtonStyleBuilder(StyleBuilderBase):

    def __init__(
            self,
            color: str = "primary",
            variant: str = "solid",
            size: str = "md",
            **kwargs
    ):
        super().__init__(
            "TButton",
            color=color,
            variant=variant,
            size=size,
            **kwargs
        )
        self._stateful_icons: dict[str, BootstrapIcon] = dict()

    @property
    def stateful_icons(self):
        return self._stateful_icons

    # ----- style builder options ------

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

    # ----- variant style builders ------

    def register_style(self):
        if self.variant() == 'solid':
            self.solid_button()
        elif self.variant() == 'outline':
            self.outline_button()
        elif self.variant() == 'ghost':
            self.ghost_button()

    def solid_button(self):
        ttk_style = self.resolve_name()
        foreground = self.theme.on_color(self.color())
        foreground_disabled = self.theme.on_surface_disabled()
        normal = self.theme.color(self.color())
        pressed = self.theme.pressed(self.color())
        hovered = self.theme.hovered(self.color())
        focused = hovered
        focused_border = self.theme.focused_border(self.color())
        disabled = self.theme.disabled(self.color())
        surface = self.theme.surface_color(self.surface())
        focused_ring = self.theme.focused_ring(self.color(), surface)

        # button element images
        normal_img = recolor_image(f'btn-{self.size()}', normal, normal, surface)
        pressed_img = recolor_image(f'btn-{self.size()}', pressed, pressed, surface)
        hovered_img = recolor_image(f'btn-{self.size()}', hovered, hovered, surface)
        focused_img = recolor_image(f'btn-{self.size()}', focused, focused_border, focused_ring)
        focused_hovered_img = recolor_image(f'btn-{self.size()}', hovered, focused_border, focused_ring)
        focused_pressed_img = recolor_image(f'btn-{self.size()}', pressed, focused_border, focused_ring)
        disabled_img = recolor_image(f'btn-{self.size()}', disabled, disabled, surface, surface)
        btn_padding = self.button_img_border()

        # button element
        self.create_element(
            ElementImage(
                f'{ttk_style}.border', normal_img, sticky="nsew", border=btn_padding, padding=btn_padding).state_specs(
                [
                    ('disabled', disabled_img),
                    ('focus pressed', focused_pressed_img),
                    ('focus hover', focused_hovered_img),
                    ('focus', focused_img),
                    ('pressed', pressed_img),
                    ('hover', hovered_img),
                ]))

        self.create_button_style()
        self.configure(
            ttk_style,
            background=surface,
            foreground=foreground,
            padding=self.button_padding(),
            stipple="gray12",
            relief='flat',
            font=self.get_font())

        self.map(ttk_style, foreground=[('disabled', foreground_disabled)], background=[('disabled', disabled)])

    def outline_button(self):
        ttk_style = self.resolve_name()
        foreground = self.theme.color(self.color())
        foreground_disabled = self.theme.disabled(self.color())
        foreground_active = self.theme.on_color(self.color())
        normal = self.theme.surface_color(self.surface())
        disabled = foreground_disabled
        pressed = self.theme.hovered(self.color())
        focused = hovered = pressed
        focused_border = self.theme.focused_border(self.color())
        surface = self.theme.surface_color(self.surface())
        focused_ring = self.theme.focused_ring(self.color(), surface)

        # button element images
        normal_img = recolor_image(f'btn-{self.size()}', normal, foreground, surface)
        pressed_img = recolor_image(f'btn-{self.size()}', pressed, pressed, surface)
        hovered_img = recolor_image(f'btn-{self.size()}', hovered, hovered, surface)
        focused_img = recolor_image(f'btn-{self.size()}', focused, focused_border, focused_ring)
        focused_hovered_img = recolor_image(f'btn-{self.size()}', hovered, focused_border, focused_ring)
        focused_pressed_img = recolor_image(f'btn-{self.size()}', pressed, focused_border, focused_ring)
        disabled_img = recolor_image(f'btn-{self.size()}', surface, disabled, surface, surface)
        btn_padding = self.button_img_border()

        # button element
        self.create_element(
            ElementImage(
                f'{ttk_style}.border', normal_img, sticky="nsew", border=btn_padding, padding=btn_padding).state_specs(
                [
                    ('disabled', disabled_img),
                    ('focus pressed', focused_pressed_img),
                    ('focus hover', focused_hovered_img),
                    ('focus', focused_img),
                    ('pressed', pressed_img),
                    ('hover', hovered_img),
                ]))

        self.create_button_style()
        self.configure(
            ttk_style,
            background=surface,
            foreground=foreground,
            padding=self.button_padding(),
            relief='flat',
            stipple="gray12",
            font=self.get_font())

        self.map(
            ttk_style,
            foreground=[
                ('disabled', foreground_disabled),
                ('focus', foreground_active),
                ('hover', foreground_active),
            ], background=[('disabled', surface)])

    def ghost_button(self):
        ttk_style = self.resolve_name()
        foreground = self.theme.color(self.color())
        foreground_disabled = self.theme.disabled(self.color())
        normal = self.theme.surface_color(self.surface())
        pressed = self.theme.subtle(self.color(), self.surface())
        focused = hovered = pressed
        surface = self.theme.surface_color(self.surface())
        focused_ring = self.theme.focused_ring(self.color(), surface)

        # button element images
        normal_img = recolor_image(f'btn-{self.size()}', normal, normal, surface)
        pressed_img = recolor_image(f'btn-{self.size()}', pressed, surface, surface)
        hovered_img = recolor_image(f'btn-{self.size()}', hovered, surface, surface)
        focused_img = recolor_image(f'btn-{self.size()}', focused, focused, focused_ring)
        focused_hovered_img = recolor_image(f'btn-{self.size()}', hovered, focused, focused_ring)
        focused_pressed_img = recolor_image(f'btn-{self.size()}', pressed, focused, focused_ring)
        disabled_img = recolor_image(f'btn-{self.size()}', surface, surface, surface, surface)
        btn_padding = self.button_img_border()

        # button element
        self.create_element(
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

        self.create_button_style()
        self.configure(
            ttk_style,
            background=surface,
            foreground=foreground,
            padding=self.button_padding(),
            relief='flat',
            stipple="gray12",
            font=self.get_font())

        self.map(ttk_style,
                 foreground=[('disabled', foreground_disabled)],
                 background=[('disabled', surface)])

    # ----- Button Style Utilities -----

    def create_button_style(self):
        ttk_style = self.resolve_name()
        self.style_layout(
            ttk_style, Element(f"{ttk_style}.border", sticky="nsew").children(
                [
                    Element("Button.padding", sticky="nsew").children(
                        [
                            Element("Button.label", sticky="")
                        ])
                ]))

    def build_icon_assets(self, icon: str):
        if self.variant() == 'solid':
            self.build_solid_icon_assets(icon)
        elif self.variant() == 'outline':
            self.build_outline_icon_assets(icon)
        elif self.variant() == 'ghost':
            self.build_ghost_icon_assets(icon)

    def build_solid_icon_assets(self, icon: str):
        foreground = self.theme.on_color(self.color())
        foreground_disabled = self.theme.on_surface_disabled()
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_outline_icon_assets(self, icon: str):
        foreground = self.theme.color(self.color())
        foreground_disabled = self.theme.disabled(self.color())
        foreground_active = self.theme.on_color(self.color())
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground_active)
        self.create_icon_asset(icon, 'pressed', foreground_active)
        self.create_icon_asset(icon, 'focus', foreground_active)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_ghost_icon_assets(self, icon: str):
        foreground = self.theme.color(self.color())
        foreground_disabled = self.theme.disabled(self.color())
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def create_icon_asset(self, icon: str, state: str, color: str):
        # create stateful icons to be mapped by the buttons event handling logic
        self._stateful_icons[state] = BootstrapIcon(icon, self.icon_font_size(), color)

    def button_padding(self) -> tuple[int, int] | tuple[int, int, int, int]:
        """Calculate button padding based on button size"""
        size = self.size()
        if size == "sm":
            return 0, 0
        elif size == "md":
            return 0, 0
        else:
            return 0, 0

    def icon_font_size(self) -> int:
        """Return the icon size scaled from font size."""
        factor = 0.72
        fnt = self.get_font()
        font_size = fnt.metrics('linespace')
        return int(font_size * factor)

    def get_font(self):
        size = self.size()
        if size == "sm":
            return nametofont("body")
        elif size == "lg":
            return nametofont("body_xl")
        else:
            return nametofont("body_lg")

    def button_img_border(self):
        size = self.size()
        if size == "sm":
            return 6
        elif size == "md":
            return 8
        else:
            return 10
