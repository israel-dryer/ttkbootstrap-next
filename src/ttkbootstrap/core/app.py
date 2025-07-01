from tkinter import Tk
from ttkbootstrap.core.libtypes import ColorThemeType
from ttkbootstrap.core.widget import BaseWidget
from ttkbootstrap.style.theme import ColorTheme
from ttkbootstrap.style.typography import Typography


class App(BaseWidget):

    def __init__(self, title="ttkbootstrap", theme: ColorThemeType = "light", use_default_fonts: bool = True):
        self._widget = Tk()
        self._surface = "base"
        super().__init__(None)

        # hide until ready to render
        self.widget.withdraw()
        self.widget.title(title)
        self._theme = ColorTheme.instance(theme)
        self.widget.configure(background=self.theme.surface_color(self.surface))

        # register fonts
        if use_default_fonts:
            Typography.use_fonts()

    @property
    def theme(self):
        return self._theme

    @property
    def master(self):
        return self.widget.master

    @property
    def tk(self):
        return self.widget.tk

    @property
    def _w(self):
        return self.widget._w

    @property
    def _last_child_ids(self):
        return self.widget._last_child_ids

    @property
    def children(self):
        return self.widget.children

    @property
    def surface(self):
        return self._surface

    @_last_child_ids.setter
    def _last_child_ids(self, value):
        self.widget._last_child_ids = value

    def run(self):
        self.widget.deiconify()
        return self.widget.mainloop()

    def quit(self):
        self.widget.quit()

    def __str__(self):
        return str(self.widget)

    def destroy(self):
        return self.widget.destroy()

    def report_callback_exception(self, a, b, c):
        return self.widget.report_callback_exception(a, b, c)