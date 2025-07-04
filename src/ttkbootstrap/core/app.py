from tkinter import Tk
from ttkbootstrap.core.libtypes import ColorMode
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.builders.window import WindowStyleBuilder
from ttkbootstrap.style.theme import ColorTheme
from ttkbootstrap.style.tokens import SurfaceToken
from ttkbootstrap.style.typography import Typography


class App(BaseWidget, ContainerMixin):

    def __init__(
            self,
            title="ttkbootstrap",
            theme: ColorMode = "light",
            use_default_fonts: bool = True,
            surface: SurfaceToken = "base"
    ):
        self._widget = Tk()
        super().__init__(None, surface=surface)
        self._style_builder = WindowStyleBuilder(self)

        # hide until ready to render
        self.widget.withdraw()
        self.widget.title(title)
        self._theme = ColorTheme.instance(theme)
        self._theme.use(theme)

        # register fonts
        if use_default_fonts:
            Typography.use_fonts()

    @property
    def theme(self):
        return self._theme

    def surface(self, value=None):
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self.theme.update_theme_styles()
            return self

    @property
    def surface_token(self):
        return self._surface_token

    def run(self):
        self.widget.deiconify()
        return self.widget.mainloop()

    def quit(self):
        self.widget.quit()

    def report_callback_exception(self, a, b, c):
        return self.widget.report_callback_exception(a, b, c)
