# geometry managers
from tkinter import Widget

# TODO remove this module when layout is fully implemented

class GeometryMixin:
    widget: Widget

    def pack(self, option=None, **kwargs):
        if option is None:
            self.widget.pack(**kwargs)
            return self
        else:
            return self.widget.pack(option)

    def pack_forget(self):
        self.widget.pack_forget()
        return self

    def grid(self, option=None, **kwargs):
        if option is None:
            self.widget.grid(**kwargs)
            return self
        else:
            return self.widget.grid(option)

    def grid_row_configure(self, index, *, option=None, **kwargs):
        if option is None:
            self.widget.rowconfigure(index, **kwargs)
            return self
        else:
            return self.widget.rowconfigure(index, option)

    def grid_column_configure(self, index, *, option=None, **kwargs):
        if option is None:
            self.widget.columnconfigure(index, **kwargs)
            return self
        else:
            return self.widget.columnconfigure(index, option)

    # def place(self, option=None, **kwargs):
    #     if option is None:
    #         self.widget.place(**kwargs)
    #         return self
    #     else:
    #         return self.widget.place(option)
