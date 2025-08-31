from ttkbootstrap.style.builders.base import StyleBuilderBase


class LabelFrameStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__("TLabelframe", **kwargs)

    def register_style(self):
        ttk_style = self.resolve_name()
        surface_token = self.surface()
        label_token = self.options.get('label_color')
        border_token = self.options.get('border_color')

        background = self.theme.color(surface_token)

        if label_token is None:
            foreground = self.theme.on_color(background)
        else:
            foreground = self.theme.color(label_token)

        if border_token is None:
            border = self.theme.border(background)
        else:
            border = self.theme.color(border_token)
        self.configure(
            ttk_style,
            background=background,
            bordercolor=border,
            lightcolor=background,
            darkcolor=background
        )
        self.configure(f"{ttk_style}.Label", foreground=foreground, background=background)
