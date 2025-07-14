import tkinter as tk
from tkinter import ttk

class ListItem(tk.Frame):

    def __init__(self, parent, title: str = None, message: str = None, badge: str = None, **kwargs):
        super().__init__(parent, **kwargs)
        self._title = tk.Label(self, text=title, font='TkCaptionFont', anchor='w')
        self._message = tk.Label(self, text=message, anchor='w')
        self._badge = tk.Label(self, text=badge, foreground='blue')

        if title:
            self._title.pack(padx=8, pady=4, fill='x')
        if message:
            self._message.pack(fill='x', expand=True)
        if badge:
            self._badge.pack(side='right', before=self._message, padx=(8, 0))
        ttk.Separator(self, orient='horizontal').pack(fill='x', expand=True)

class List(tk.Frame):

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self._scroll = tk.Scrollbar(self, orient='vertical', command=self._canvas.yview)
        self._frame = tk.Frame(self._canvas, padx=8, pady=8)

        self._frame.bind('<Configure>', self._frame_configure)
        self._canvas.bind('<Configure>', self._canvas_configure)

        self._items = []

        self._canvas_window = self._canvas.create_window((0, 0), window=self._frame, anchor='nw')
        self._canvas.configure(yscrollcommand=self._scroll.set)
        self._canvas.pack(side='left', fill='both', expand=True)
        self._scroll.pack(side='right', fill='y')


    def _frame_configure(self, _):
        self._canvas.configure(scrollregion=self._canvas.bbox('all'))

    def _canvas_configure(self, e):
        canvas_width = e.width
        self._canvas.itemconfig(self._canvas_window, width=canvas_width)

    def add(self, *, title=None, message=None, badge=None):
        item = ListItem(self._frame, title, message, badge)
        item.pack(fill='x', expand=True)
        self._items.append(item)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Demo Listbox')

    l = List(root)

    for x in range(1, 50):
        l.add(title=f"Item {x}", message="Something here", badge=x)
    l.pack(fill='both', expand=True)

    root.mainloop()
