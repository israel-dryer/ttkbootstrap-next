from tkinter import ttk

from ttkbootstrap.core import App
from ttkbootstrap.widgets.button import Button
from ttkbootstrap.style.style import Style

app = App("Button Demo", theme="light")

style = Style()

Button(app, "Primary", color="primary").pack(padx=16, pady=16)
Button(app, "Secondary", color="secondary").pack(padx=16, pady=16)
Button(app, "Success", color="success").pack(padx=16, pady=16)
Button(app, "Warning", color="warning").pack(padx=16, pady=16)
Button(app, "Danger", color="danger").pack(padx=16, pady=16)
Button(app, "Info", color="info").pack(padx=16, pady=16)
Button(app, "Light", color="light").pack(padx=16, pady=16)
Button(app, "Dark", color="dark").pack(padx=16, pady=16)


def get_style():
    print(btn.configure('style'))


app.run()
