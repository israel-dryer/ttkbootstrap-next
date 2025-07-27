from tkinter import TclError
from tkinter.font import nametofont

from ttkbootstrap.icons import BootstrapIcon
from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import ElementImage, Element
from ttkbootstrap.style.tokens import ForegroundColor, SurfaceColor
from ttkbootstrap.style.utils import recolor_image

_images = []


class LabelStyleBuilder(StyleBuilderBase):

    def __init__(self, foreground=None, background=None, variant="default", **kwargs):
        super().__init__(
            "TLabel",
            foreground=foreground,
            background=background,
            variant=variant,
            **kwargs)
        self._stateful_icons: dict[str, BootstrapIcon] = dict()

    @property
    def stateful_icons(self):
        return self._stateful_icons

    def foreground(self, value: ForegroundColor = None):
        if value is None:
            return self.options.get('foreground', None)
        else:
            self.options.update(foreground=value)
            return self

    def background(self, value: SurfaceColor = None):
        if value is None:
            return self.options.get('background', None)
        else:
            self.options.update(background=value)
            return self

    def variant(self, value: str = None):
        if value is None:
            return self.options.get('variant', None)
        else:
            self.options.update(variant=value)
            return self

    def select_background(self, value: str = None):
        if value is None:
            return self.options.get('select_background') or 'primary'
        else:
            self.options.update(select_background=value)
            return self

    def register_style(self):
        if self.variant().endswith('fix'):
            self.build_addon_style()
        elif self.variant() == 'list':
            self.build_list_style()
        else:
            self.build_default_style()

    def build_default_style(self):
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        foreground_token = self.foreground()
        background_token = self.background()

        if background_token is None:
            background = self.theme.color(surface_token)
        else:
            background = self.theme.color(background_token)

        if foreground_token is None:
            foreground = self.theme.on_color(background)
        else:
            try:
                foreground = self.theme.color(foreground_token, "text")
            except TclError:
                foreground = self.foreground()
        self.configure(ttk_style, background=background, foreground=foreground)

    def build_addon_style(self):
        theme = self.theme
        ttk_style = self.resolve_name()
        surface_token = self.surface()

        surface = theme.color(surface_token)
        border = self.theme.border(surface)
        foreground = theme.on_color(surface)
        normal = self.theme.disabled()

        # button element images
        normal_img = recolor_image(f'input-{self.variant()}', normal, border)
        img_padding = 8

        # button element
        self.create_element(
            ElementImage(
                f'{ttk_style}.border', normal_img, sticky="nsew", border=img_padding, padding=img_padding))

        ttk_style = self.resolve_name()
        self.style_layout(
            ttk_style, Element(f"{ttk_style}.border", sticky="nsew").children(
                [
                    Element("Label.padding", sticky="nsew").children(
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
            padding=0
        )

    def build_list_style(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        background = theme.color(self.surface())
        background_hover = theme.elevate(background, 1)
        background_pressed = theme.elevate(background, 2)
        background_selected = theme.color(self.select_background())
        background_selected_hover = theme.hover(background_selected)
        foreground_token = self.foreground()
        if foreground_token is None:
            foreground = self.theme.on_color(background)
        else:
            try:
                foreground = self.theme.color(foreground_token, "text")
            except TclError:
                foreground = self.foreground()

        foreground_selected = theme.on_color(background_selected)
        self.configure(ttk_style, background=background, foreground=foreground)
        self.map(
            ttk_style,
            background=[
                ('selected hover', background_selected_hover),
                ('selected', background_selected),
                ('pressed', background_pressed),
                ('hover', background_hover)],
            foreground=[('selected', foreground_selected)]
        )

    def build_icon_assets(self, icon: dict):
        if icon is None: return
        if self.variant() == 'list':
            self.build_list_icon_assets(icon)
        else:
            self.build_default_icon_assets(icon)

    def build_default_icon_assets(self, icon: dict):
        background = self.theme.color(self.surface())
        if self.foreground() is None:
            foreground = self.theme.on_color(background)
        else:
            try:
                foreground = self.theme.color(self.foreground(), "text")
            except TclError:
                foreground = self.foreground()

        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground)

    def create_icon_asset(self, icon: dict, state: str, color: str):
        # create stateful icons to be mapped by the buttons event handling logic
        options = dict(icon)
        options.setdefault('size', self.icon_font_size())
        options.setdefault('color', color)
        self._stateful_icons[state] = BootstrapIcon(**options)

    def build_list_icon_assets(self, icon: dict):
        background = self.theme.color(self.surface())
        if self.foreground() is None:
            foreground = self.theme.on_color(background)
        else:
            try:
                foreground = self.theme.color(self.foreground(), "text")
            except TclError:
                foreground = self.foreground()

        background_selected = self.theme.color(self.select_background())
        foreground_selected = self.theme.on_color(background_selected)

        self.create_icon_asset(icon, 'normal', foreground)
        self.create_icon_asset(icon, 'hover', foreground)
        self.create_icon_asset(icon, 'pressed', foreground)
        self.create_icon_asset(icon, 'focus', foreground)
        self.create_icon_asset(icon, 'disabled', foreground)
        self.create_icon_asset(icon, 'selected', foreground_selected)

    @classmethod
    def icon_font_size(cls) -> int:
        """Return the icon size scaled from font size."""
        factor = 0.9
        fnt = nametofont('body-lg')
        font_size = fnt.metrics('linespace')
        return int(font_size * factor)
