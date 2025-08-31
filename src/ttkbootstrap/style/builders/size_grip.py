from ttkbootstrap.style.builders.base import StyleBuilderBase


class SizeGripStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__('TSizegrip', **kwargs)

    def register_style(self):
        ttk_style = self.resolve_name()
        background = self.theme.color(self.surface())
        color_token = self.options('color')
        if color_token is None:
            foreground = self.theme.on_color(background)
        else:
            foreground = self.theme.color(color_token)

        # TODO this needs a custom image layout for styling
        self.configure(ttk_style, background=background, foreground=foreground)
