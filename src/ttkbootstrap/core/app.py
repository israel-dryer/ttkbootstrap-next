from tkinter import Tk
from ttkbootstrap.core.libtypes import ColorMode
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.widget import BaseWidget, layout_context_stack, set_default_root
from ttkbootstrap.style.builders.window import WindowStyleBuilder
from ttkbootstrap.style.theme import ColorTheme
from ttkbootstrap.style.tokens import SurfaceColor
from ttkbootstrap.style.typography import Typography


class App(BaseWidget, ContainerMixin):

    def __init__(
            self,
            title="ttkbootstrap",
            theme: ColorMode = "light",
            use_default_fonts: bool = True,
            surface: SurfaceColor = "background"
    ):
        set_default_root(self)
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

        self._style_builder.register_style()

    def __enter__(self):
        layout_context_stack().append(self)
        return self

    def __exit__(self, *args):
        layout_context_stack().pop()

    @property
    def theme(self):
        return self._theme

    def geometry(self, *args):
        self.widget.geometry(*args)
        return self

    def surface(self, value=None):
        if value is None:
            return self._surface_token
        else:
            self._surface_token = value
            self.theme.update_theme_styles()
            return self

    @property
    def _bind(self, *args):
        return self.widget._bind

    @property
    def surface_token(self):
        return self._surface_token

    def run(self):
        self.widget.update_idletasks()
        self.widget.deiconify()
        return self.widget.mainloop()

    def quit(self):
        self.widget.quit()

    def report_callback_exception(self, a, b, c):
        return self.widget.report_callback_exception(a, b, c)
