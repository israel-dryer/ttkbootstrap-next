from tkinter.font import nametofont

from .base import StyleBuilderBase
from ..element import Element, ElementImage
from ..tokens import ButtonVariant, SemanticColor
from ..utils import recolor_image
from ...core.libtypes import ButtonSize
from ...icons import BootstrapIcon

_images = []


class ButtonStyleBuilder(StyleBuilderBase):

    def __init__(self, color="primary", variant="solid", **kwargs):
        super().__init__(
            "TButton",
            color=color,
            variant=variant,
            **kwargs
        )
        self._stateful_icons: dict[str, BootstrapIcon] = dict()

    @property
    def stateful_icons(self):
        return self._stateful_icons

    # ----- style builder options ------

    def color(self, value: SemanticColor = None):
        if value is None:
            return self.options.get('color') or 'primary'
        else:
            self.options.update(color=value)
            return self

    def variant(self, value: ButtonVariant = None):
        if value is None:
            return self.options.get('variant') or 'solid'
        else:
            self.options.update(variant=value)
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
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        color_token = self.color()

        surface = theme.color(surface_token)
        normal = theme.color(color_token)
        foreground = theme.on_color(normal)
        foreground_disabled = theme.disabled("text")
        pressed = theme.active(normal)
        hovered = theme.hover(normal)
        focused = hovered
        focused_border = theme.focus_border(normal)
        disabled = theme.disabled()
        focused_ring = theme.focus_ring(normal, surface)

        # button element images
        normal_img = recolor_image(f'button', normal, normal, surface)
        pressed_img = recolor_image(f'button', pressed, pressed, surface)
        hovered_img = recolor_image(f'button', hovered, hovered, surface)
        focused_img = recolor_image(f'button', focused, focused_border, focused_ring)
        focused_hovered_img = recolor_image(f'button', hovered, focused_border, focused_ring)
        focused_pressed_img = recolor_image(f'button', pressed, focused_border, focused_ring)
        disabled_img = recolor_image(f'button', disabled, disabled, surface, surface)
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
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        color_token = self.color()

        surface = theme.color(surface_token)
        foreground = theme.color(color_token)
        foreground_disabled = theme.disabled("text")
        foreground_active = theme.on_color(foreground)
        normal = surface
        disabled = foreground_disabled
        pressed = theme.hover(foreground)
        focused = hovered = pressed
        focused_border = theme.focus_border(foreground)
        focused_ring = theme.focus_ring(foreground, surface)

        # button element images
        normal_img = recolor_image(f'button', normal, foreground, surface)
        pressed_img = recolor_image(f'button', pressed, pressed, surface)
        hovered_img = recolor_image(f'button', hovered, hovered, surface)
        focused_img = recolor_image(f'button', focused, focused_border, focused_ring)
        focused_hovered_img = recolor_image(f'button', hovered, focused_border, focused_ring)
        focused_pressed_img = recolor_image(f'button', pressed, focused_border, focused_ring)
        disabled_img = recolor_image(f'button', surface, disabled, surface, surface)
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
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        color_token = self.color()

        surface = theme.color(surface_token)
        foreground = theme.color(color_token)
        foreground_disabled = theme.disabled("text")
        normal = surface
        pressed = theme.subtle(color_token, surface)
        focused = hovered = pressed
        focused_ring = theme.focus_ring(focused, surface)

        # button element images
        normal_img = recolor_image(f'button', normal, normal, surface, surface)
        pressed_img = recolor_image(f'button', pressed, surface, surface, surface)
        hovered_img = recolor_image(f'button', hovered, surface, surface, surface)
        focused_img = recolor_image(f'button', focused, focused, focused_ring, surface)
        focused_hovered_img = recolor_image(f'button', hovered, focused, focused_ring, surface)
        focused_pressed_img = recolor_image(f'button', pressed, focused, focused_ring, surface)
        disabled_img = recolor_image(f'button', surface, surface, surface, surface)
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

        self.map(
            ttk_style,
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
        color_token = self.color()
        background = self.theme.color(color_token)
        foreground = self.theme.on_color(background)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_outline_icon_assets(self, icon: str):
        color_token = self.color()
        accent = self.theme.color(color_token)
        foreground_active = self.theme.on_color(accent)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', accent)
        self.create_icon_asset(icon, 'hover', foreground_active)
        self.create_icon_asset(icon, 'pressed', foreground_active)
        self.create_icon_asset(icon, 'focus', foreground_active)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_ghost_icon_assets(self, icon: str):
        color_token = self.color()
        foreground = self.theme.color(color_token)
        foreground_disabled = self.theme.disabled("text")
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
            return nametofont("body-xl")
        else:
            return nametofont("body-lg")

    def button_img_border(self):
        size = self.size()
        if size == "sm":
            return 6
        elif size == "md":
            return 8
        else:
            return 10
