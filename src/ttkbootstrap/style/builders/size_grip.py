from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.types import ForegroundColor


class SizeGripStyleBuilder(StyleBuilderBase):

    def __init__(self, color: ForegroundColor = None):
        super().__init__('TSizegrip', color=color)

    def color(self, value: ForegroundColor = None):
        if value is None:
            return self.options.get('value', None)
        else:
            self.options.update(color=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        background = self.theme.color(self.surface())
        color_token = self.color()
        if color_token is None:
            foreground = self.theme.on_color(background)
        else:
            foreground = self.theme.color(color_token)

        # TODO this needs a custom image layout for styling
        self.configure(ttk_style, background=background, foreground=foreground)
