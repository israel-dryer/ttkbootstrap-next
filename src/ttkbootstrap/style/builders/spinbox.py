from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import Element, ElementImage
from ttkbootstrap.style.utils import recolor_image


class SpinBoxStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__(f"TSpinbox", **kwargs)

    def register_style(self):
        ttk_style = self.resolve_name()
        surface = self.theme.color(self.surface())
        disabled_bg = self.theme.disabled('background')
        disabled_fg = self.theme.disabled('text')
        foreground = self.theme.on_color(surface)

        normal_img = recolor_image(f'input-inner', surface)
        self.create_element(ElementImage(f'{ttk_style}.field', normal_img, sticky="nsew"))
        self.style_layout(
            ttk_style, Element(f'{ttk_style}.field').children(
                [
                    Element('Spinbox.padding', sticky="ew").children(
                        [
                            Element('Spinbox.textarea', sticky="nsew")
                        ])
                ]))

        self.configure(
            ttk_style,
            relief='flat',
            foreground=foreground,
            background=surface,
            fieldbackground=surface,
            selectborderwidth=0,
            bordercolor=surface,
            darkcolor=surface,
            lightcolor=surface,
            insertcolor=foreground,
            padding=(8, 0),
            selectforeground=self.theme.on_color(self.theme.color('primary')),
            selectbackground=self.theme.color('primary')
        )

        self.map(
            ttk_style,
            background=[('disabled', disabled_bg)],
            fieldbackground=[('disabled', disabled_bg)],
            selectforeground=[],
            selectbackground=[],
            bordercolor=[('disabled', disabled_bg)],
            darkcolor=[('disabled', disabled_bg)],
            lightcolor=[('disabled', disabled_bg)],
            foreground=[('disabled !readonly', disabled_fg)]
        )
