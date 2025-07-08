# import tkinter as tk
#
#
# root = tk.Tk()
#
# c = tk.Canvas()
# c.pack()
# item = c.create_text(10, 10, text="Hello world")
# print(item)
# print(type(item))
#
# root.mainloop()
from ttkbootstrap.core import App
from ttkbootstrap.widgets import Button, Canvas

app = App("Canvas Demo")

Button(app, "Hello", on_click=lambda: app.theme.use('dark')).pack(padx=16, pady=10)

canvas = Canvas(app).pack()
canvas.draw_text(100, 100, "Hello World")

app.run()