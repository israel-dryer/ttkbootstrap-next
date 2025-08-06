from tkinter.font import nametofont

from .base import StyleBuilderBase
from ..element import Element, ElementImage
from ..tokens import ButtonVariant, SemanticColor
from ..utils import recolor_image
from ttkbootstrap.common.types import ButtonSize
from ...icons import BootstrapIcon

_images = []


class IconButtonStyleBuilder(StyleBuilderBase):

    def __init__(self, color="primary", variant="solid", size="md", **kwargs):
        super().__init__(
            "Icon.TButton",
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

    def select_background(self, value: SemanticColor = None):
        if value is None:
            return self.options.get('select_background') or 'primary'
        else:
            self.options.update(select_background=value)
            return self

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

    def size(self, value: ButtonSize = None):
        if value is None:
            return self.options.get('size') or 'md'
        else:
            self.options.update(size=value)
            return self

    # ----- variant style builders ------

    def register_style(self):
        if self.variant() == 'outline':
            self.outline_button()
        elif self.variant() == 'ghost':
            self.ghost_button()
        elif self.variant() == 'text':
            self.text_button()
        elif self.variant().endswith('fix'):
            self.field_addon_button()
        elif self.variant() == 'list':
            self.list_button()
        else:
            self.solid_button()

    def list_button(self):
        theme = self.theme
        ttk_style = self.resolve_name()

        surface = theme.color(self.surface())
        background_hover = theme.elevate(surface, 1)
        background_pressed = theme.elevate(surface, 2)
        background_selected = theme.color(self.select_background())
        background_selected_hover = theme.hover(background_selected)

        # button element
        self.style_layout(ttk_style, Element('Label.border', sticky="nsew").children([
            Element('Label.padding', sticky="nsew").children([
                Element("Label.label", sticky="")
            ])
        ]))

        self.configure(
            ttk_style,
            background=surface,
            padding=0,
            relief='flat',
            stipple="gray12",
            font=self.get_font())

        self.map(
            ttk_style,
            foreground=[],
            background=[
                ('selected hover', background_selected_hover),
                ('selected', background_selected),
                ('pressed', background_pressed),
                ('hover', background_hover)])

    def solid_button(self):
        theme = self.theme
        ttk_style = self.resolve_name()

        normal = theme.color(self.color())
        pressed = theme.active(normal)
        hovered = theme.hover(normal)
        focused = hovered
        focused_border = theme.focus_border(normal)
        disabled = theme.disabled()
        surface = theme.color(self.surface())
        focused_ring = theme.focus_ring(normal, surface)

        foreground = theme.on_color(normal)
        foreground_disabled = theme.disabled("text")

        # button element images
        normal_img = recolor_image(f'icon-button', normal, normal, surface)
        pressed_img = recolor_image(f'icon-button', pressed, pressed, surface)
        hovered_img = recolor_image(f'icon-button', hovered, hovered, surface)
        focused_img = recolor_image(f'icon-button', focused, focused_border, focused_ring)
        focused_hovered_img = recolor_image(f'icon-button', hovered, focused_border, focused_ring)
        focused_pressed_img = recolor_image(f'icon-button', pressed, focused_border, focused_ring)
        disabled_img = recolor_image(f'icon-button', disabled, disabled, surface, surface)
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

        self.map(ttk_style, foreground=[('disabled', foreground_disabled)], background=[('disabled', disabled)])

    def outline_button(self):
        theme = self.theme
        ttk_style = self.resolve_name()

        surface = self.theme.color(self.surface())
        foreground = theme.color(self.color())
        foreground_disabled = theme.disabled()
        foreground_active = theme.on_color(foreground)
        normal = surface
        disabled = foreground_disabled
        pressed = theme.hover(foreground)
        focused = hovered = pressed
        focused_border = theme.focus_border(foreground)
        focused_ring = theme.focus_ring(foreground, surface)

        # button element images
        normal_img = recolor_image(f'icon-button', normal, foreground, surface)
        pressed_img = recolor_image(f'icon-button', pressed, pressed, surface)
        hovered_img = recolor_image(f'icon-button', hovered, hovered, surface)
        focused_img = recolor_image(f'icon-button', focused, focused_border, focused_ring)
        focused_hovered_img = recolor_image(f'icon-button', hovered, focused_border, focused_ring)
        focused_pressed_img = recolor_image(f'icon-button', pressed, focused_border, focused_ring)
        disabled_img = recolor_image(f'icon-button', surface, disabled, surface, surface)
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

    def text_button(self):
        theme = self.theme
        ttk_style = self.resolve_name()

        surface = theme.color(self.surface())

        # button element
        self.style_layout(ttk_style, Element('Label.border', sticky="nsew").children([
            Element('Label.padding', sticky="nsew").children([
                Element("Label.label", sticky="")
            ])
        ]))

        self.configure(
            ttk_style,
            background=surface,
            padding=0,
            relief='flat',
            stipple="gray12",
            font=self.get_font())

        self.map(ttk_style, foreground=[], background=[])


    def ghost_button(self):
        theme = self.theme
        ttk_style = self.resolve_name()

        surface = theme.color(self.surface())
        foreground = theme.color(self.color())
        foreground_disabled = theme.disabled("text")
        normal = surface
        pressed = self.theme.subtle(self.color(), surface)
        focused = hovered = pressed
        focused_ring = self.theme.focus_ring(foreground, surface)

        # button element images
        normal_img = recolor_image(f'icon-button', normal, normal, surface, surface)
        pressed_img = recolor_image(f'icon-button', pressed, surface, surface, surface)
        hovered_img = recolor_image(f'icon-button', hovered, surface, surface, surface)
        focused_img = recolor_image(f'icon-button', focused, focused, focused_ring, surface)
        focused_hovered_img = recolor_image(f'icon-button', hovered, focused, focused_ring, surface)
        focused_pressed_img = recolor_image(f'icon-button', pressed, focused, focused_ring, surface)
        disabled_img = recolor_image(f'icon-button', surface, surface, surface, surface)
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

    def field_addon_button(self):
        theme = self.theme
        ttk_style = self.resolve_name()
        surface = theme.color(self.surface())
        border = self.theme.border(surface)
        foreground = theme.color(self.color())
        foreground_disabled = theme.disabled("text")
        normal = self.theme.disabled()
        pressed = self.theme.subtle('secondary', surface)
        focused = hovered = pressed

        # button element images
        normal_img = recolor_image(f'input-{self.variant()}', normal, border)
        pressed_img = recolor_image(f'input-{self.variant()}', pressed, border, surface, surface)
        hovered_img = recolor_image(f'input-{self.variant()}', hovered, border, hovered, surface)
        focused_img = recolor_image(f'input-{self.variant()}', focused, border, focused, surface)
        focused_hovered_img = recolor_image(f'input-{self.variant()}', hovered, border, focused, surface)
        focused_pressed_img = recolor_image(f'input-{self.variant()}', pressed, border, focused, surface)
        disabled_img = recolor_image(f'input-{self.variant()}', normal, border, surface, surface)
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

    def build_icon_assets(self, icon: dict):
        if self.variant() == 'text':
            self.build_text_icon_assets(icon)
        elif self.variant() == 'outline':
            self.build_outline_icon_assets(icon)
        elif self.variant() == "ghost":
            self.build_ghost_icon_assets(icon)
        elif self.variant().endswith('fix'):
            self.build_addon_icon_assets(icon)
        elif self.variant() == 'list':
            self.build_list_icon_assets(icon)
        else:
            self.build_solid_icon_assets(icon)

    def build_solid_icon_assets(self, icon: dict):
        color_token = self.color()
        background = self.theme.color(color_token)
        foreground = self.theme.on_color(background)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_outline_icon_assets(self, icon: dict):
        color_token = self.color()
        accent = self.theme.color(color_token)
        foreground_active = self.theme.on_color(accent)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', accent)
        self.create_icon_asset(icon, 'hover', foreground_active)
        self.create_icon_asset(icon, 'pressed', foreground_active)
        self.create_icon_asset(icon, 'focus', foreground_active)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_ghost_icon_assets(self, icon: dict):
        color_token = self.color()
        foreground = self.theme.color(color_token)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_text_icon_assets(self, icon: dict):
        surface = self.theme.color(self.surface())
        foreground = self.theme.on_color(surface)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_addon_icon_assets(self, icon: dict):
        surface = self.theme.color(self.surface())
        foreground = self.theme.on_color(surface)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_list_icon_assets(self, icon: dict):
        icon['size'] = 14
        background = self.theme.color(self.surface())
        background_selected = self.theme.color(self.select_background())
        foreground = self.theme.on_color(background)
        foreground_selected = self.theme.on_color(background_selected)
        foreground_disabled = self.theme.disabled("text")

        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)
        self.create_icon_asset(icon, 'selected', foreground_selected)

    def create_icon_asset(self, icon: dict, state: str, color: str):
        # create stateful icons to be mapped by the buttons event handling logic
        options = dict(icon)
        options.setdefault('color', color)
        options.setdefault('size', self.icon_font_size())
        self._stateful_icons[state] = BootstrapIcon(**options)

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
        factor = 0.9
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
