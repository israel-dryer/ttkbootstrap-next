from tkinter.font import nametofont

from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import Element, ElementImage
from ttkbootstrap.style.utils import recolor_image
from ttkbootstrap.icons import BootstrapIcon

_images = []


class ButtonStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__("TButton", **kwargs)

        # default options
        self.options.set_defaults(
            color='primary',
            variant='solid',
            size='md',
            icon_only=False,
            select_background='primary')

        self._stateful_icons: dict[str, BootstrapIcon] = dict()

    @property
    def stateful_icons(self):
        return self._stateful_icons

    # ----- variant style builders ------

    def register_style(self):
        variant = self.options('variant')
        if variant == 'outline':
            self.build_outline_style()
        elif variant == 'ghost':
            self.build_ghost_style()
        elif variant.endswith('fix'):
            self.build_field_addon_style()
        elif variant == 'text':
            self.build_text_style()
        elif variant == 'list':
            self.build_list_style()
        else:
            self.build_default_style()

    def build_default_style(self):
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        color_token = self.options('color')

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
            stipple="gray12",
            relief='flat',
            padding=0,
            font=self.get_font())

        self.map(ttk_style, foreground=[('disabled', foreground_disabled)], background=[('disabled', disabled)])

    def build_outline_style(self):
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        color_token = self.options('color')

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
            relief='flat',
            stipple="gray12",
            padding=0,
            font=self.get_font())

        self.map(
            ttk_style,
            foreground=[
                ('disabled', foreground_disabled),
                ('focus', foreground_active),
                ('hover', foreground_active),
            ], background=[('disabled', surface)])

    def build_ghost_style(self):
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        color_token = self.options('color')

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
            relief='flat',
            stipple="gray12",
            padding=0,
            font=self.get_font())

        self.map(
            ttk_style,
            foreground=[('disabled', foreground_disabled)],
            background=[('disabled', surface)])

    def build_field_addon_style(self):
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        variant = self.options('variant')

        surface = theme.color(surface_token)
        border = self.theme.border(surface)
        foreground = theme.on_color(surface)
        foreground_disabled = theme.disabled("text")
        normal = self.theme.disabled()
        pressed = theme.subtle('secondary', surface)
        focused = hovered = pressed

        # button element images
        normal_img = recolor_image(f'input-{variant}', normal, border)
        pressed_img = recolor_image(f'input-{variant}', pressed, border, surface, surface)
        hovered_img = recolor_image(f'input-{variant}', hovered, border, surface, surface)
        focused_img = recolor_image(f'input-{variant}', focused, border, focused, surface)
        focused_hovered_img = recolor_image(f'input-{variant}', hovered, border, focused, surface)
        focused_pressed_img = recolor_image(f'input-{variant}', pressed, border, focused, surface)
        disabled_img = recolor_image(f'input-{variant}', normal, border, surface, surface)
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
            relief='flat',
            stipple="gray12",
            padding=0,
            font=self.get_font())

        self.map(
            ttk_style,
            foreground=[('disabled', foreground_disabled)],
            background=[('disabled', surface)])

    def build_text_style(self):
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        color_token = self.options('color')

        surface = theme.color(surface_token)
        foreground = theme.color(color_token)
        foreground_disabled = theme.disabled("text")

        self.style_layout(
            ttk_style, Element('Label.border', sticky="nsew").children(
                [
                    Element('Label.padding', sticky="nsew").children(
                        [
                            Element("Label.label", sticky="")
                        ])
                ]))

        self.configure(
            ttk_style,
            background=surface,
            foreground=foreground,
            relief='flat',
            stipple="gray12",
            padding=0,
            font=self.get_font())
        self.map(ttk_style, foreground=[('disabled', foreground_disabled)], background=[])

    def build_list_style(self):
        theme = self.theme
        ttk_style = self.resolve_name()

        surface = theme.color(self.surface())
        background_hover = theme.elevate(surface, 1)
        background_pressed = theme.elevate(surface, 2)
        background_selected = theme.color(self.options('select_background'))
        background_selected_hover = theme.hover(background_selected)

        # button element
        self.style_layout(
            ttk_style, Element('Label.border', sticky="nsew").children(
                [
                    Element('Label.padding', sticky="nsew").children(
                        [
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
        variant = self.options('variant')
        if variant == 'solid':
            self.build_solid_icon_assets(icon)
        elif variant == 'outline':
            self.build_outline_icon_assets(icon)
        elif variant == 'ghost':
            self.build_ghost_icon_assets(icon)
        elif variant.endswith('fix'):
            self.build_addon_icon_assets(icon)
        elif variant == 'list':
            self.build_list_icon_assets(icon)

    def build_text_icon_assets(self, icon):
        surface = self.theme.color(self.surface())
        foreground = self.theme.on_color(surface)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_solid_icon_assets(self, icon: dict):
        color_token = self.options('color')
        background = self.theme.color(color_token)
        foreground = self.theme.on_color(background)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_outline_icon_assets(self, icon: dict):
        color_token = self.options('color')
        accent = self.theme.color(color_token)
        foreground_active = self.theme.on_color(accent)
        foreground_disabled = self.theme.disabled("text")
        self.create_icon_asset(icon, 'normal', accent)
        self.create_icon_asset(icon, 'hover', foreground_active)
        self.create_icon_asset(icon, 'pressed', foreground_active)
        self.create_icon_asset(icon, 'focus', foreground_active)
        self.create_icon_asset(icon, 'disabled', foreground_disabled)

    def build_ghost_icon_assets(self, icon: dict):
        color_token = self.options('color')
        foreground = self.theme.color(color_token)
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
        background_selected = self.theme.color(self.options('select_background'))
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

    def icon_font_size(self) -> int:
        """Return the icon size scaled from font size."""
        factor = 0.9 if self.options('icon_only') else 0.72
        fnt = self.get_font()
        font_size = fnt.metrics('linespace')
        return int(font_size * factor)

    def get_font(self):
        size = self.options("size")
        if size == "sm":
            return nametofont("body")
        elif size == "lg":
            return nametofont("body-xl")
        else:
            return nametofont("body-lg")

    def button_img_border(self):
        size = self.options("size")
        if size == "sm":
            return 6
        elif size == "md":
            return 8
        else:
            return 10
