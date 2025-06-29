from tkinter import Tk
import tkinter as tk

from ttkbootstrap.style.typography import Typography


class App:

    def __init__(self, title="ttkbootstrap", use_default_fonts: bool = True):
        self._widget = Tk()

        # hide until ready to render
        self.widget.withdraw()
        self.widget.title(title)

        # register fonts
        if use_default_fonts:
            Typography.use_fonts()

    @property
    def widget(self):
        return self._widget

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
