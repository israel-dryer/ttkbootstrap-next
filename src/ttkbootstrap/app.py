from tkinter import Tk
from ttkbootstrap.style.types import ColorMode
from ttkbootstrap.core.mixins.container import ContainerMixin
from ttkbootstrap.core.base_widget_alt import BaseWidget
from ttkbootstrap.layouts.constants import set_default_root, layout_context_stack
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
            surface: SurfaceColor = "background",
            fullscreen: bool = False,
            geometry: str = None # must be of format: 800x600 or +300+200 or 800x600+300+200
        ):
        super().__init__(Tk, dict(), surface=surface, auto_mount=False, mountable=True)
        if geometry:
            self.widget.geometry(geometry)

        if fullscreen:
            self.widget.attributes('-fullscreen', True)

        set_default_root(self)
        # set layout for window container
        self._widget.rowconfigure(0, weight=1)
        self._widget.columnconfigure(0, weight=1)
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

    def add(self, widget, **overrides):
        """
        Mount a direct child into the root grid. If the child did not specify
        sticky, default to 'nsew' so it fills the window. Allows row/col overrides.
        """
        opts = getattr(widget, "_layout_options", {}).copy()

        row = overrides.pop("row", opts.pop("row", 0))
        col = overrides.pop("column", opts.pop("column", opts.pop("col", 0)))
        sticky = overrides.pop("sticky", opts.pop("sticky", "nsew"))

        widget.mount(row=row, column=col, sticky=sticky, **overrides)
        return self

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
