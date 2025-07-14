from tkinter import TclError

from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import ElementImage, Element
from ttkbootstrap.style.tokens import ForegroundColor, SurfaceColor
from ttkbootstrap.style.utils import recolor_image


class LabelStyleBuilder(StyleBuilderBase):

    def __init__(self, foreground=None, background=None, variant="default", **kwargs):
        super().__init__(
            "TLabel",
            foreground=foreground,
            background=background,
            variant=variant,
            **kwargs)

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

    def register_style(self):
        if self.variant().endswith('fix'):
            self.build_addon_style()
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
