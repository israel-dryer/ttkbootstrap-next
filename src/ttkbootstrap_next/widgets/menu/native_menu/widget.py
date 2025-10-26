import tkinter as tk

from ttkbootstrap_next.core.base_widget import BaseWidget
from ttkbootstrap_next.widgets.menu.native_menu.style import NativeMenuStyleBuilder


class NativeMenu(BaseWidget):
    widget: tk.Menu

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent=parent,
            tk_widget=tk.Menu,
            tk_widget_options=dict(**kwargs),
            tk_layout_options=dict()
        )
        self._style_builder = NativeMenuStyleBuilder(self.widget)
        self.update_style()

    def activate(self, index):
        self.widget.activate(index)
        return self

    def add(self, item_type, **options):
        self.widget.add(item_type, **options)
        return self

    def add_cascade(self, **options):
        self.widget.add_cascade(**options)
        return self

    def add_checkbutton(self, **options):
        self.widget.add_checkbutton(**options)
        return self

    def add_command(self, **options):
        self.widget.add_command(**options)
        return self

    def add_radiobutton(self, **options):
        self.widget.add_radiobutton(**options)
        return self

    def add_separator(self, **options):
        self.widget.add_separator(**options)
        return self

    def insert(self, index, item_type, **options):
        self.widget.insert(index, item_type, **options)
        return self

    def insert_cascade(self, index, **options):
        self.widget.insert_cascade(index, **options)
        return self

    def insert_checkbutton(self, index, **options):
        self.widget.insert_checkbutton(index, **options)
        return self

    def insert_command(self, index, **options):
        self.widget.insert_command(index, **options)
        return self

    def insert_radiobutton(self, index, **options):
        self.widget.insert_radiobutton(index, **options)
        return self

    def insert_separator(self, index, **options):
        self.widget.insert_separator(index, **options)
        return self

    def delete(self, index1, index2=None):
        self.widget.delete(index1, index2)
        return self

    def item_configure(self, index, option=None, **kwargs):
        if option is None:
            self.widget.entryconfigure(index, **kwargs)
            return self
        else:
            return self.widget.entrycget(index, option)

    def index(self, index):
        return self.widget.index(index)

    def invoke(self, index):
        return self.widget.invoke(index)

    def show(self, x, y):
        self.widget.post(x, y)
        return self

    def hide(self):
        self.widget.unpost()
        return self

    def type(self, index):
        return self.widget.type(index)

    def xposition(self, index):
        return self.widget.xposition(index)

    def yposition(self, index):
        return self.widget.yposition(index)

    # alias
    post = show
    unpost = hide
