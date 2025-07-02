from tkinter import ttk

from ttkbootstrap.core import App
from ttkbootstrap.widgets.button import Button
from ttkbootstrap.style.style import Style

app = App("Button Demo", theme="light")

style = Style()

b1 = Button(app, "Primary", color="primary", icon="house").pack(padx=16, pady=16).disable()
b2 = Button(app, "Primary", color="primary", icon="house").pack(padx=16, pady=16)
Button(app, "Primary", color="primary").pack(padx=16, pady=16)
Button(app, "Secondary", color="secondary", size="lg", icon="house").pack(padx=16, pady=16)
Button(app, "Success", color="success", size="sm", icon="chevron-right", compound="right").pack(padx=16, pady=16)
Button(app, "Warning", color="warning").pack(padx=16, pady=16)
Button(app, "Danger", color="danger").pack(padx=16, pady=16)
Button(app, "Info", color="info").pack(padx=16, pady=16)
lt = Button(app, "Light", color="light").pack(padx=16, pady=16)
tb = Button(app, "Dark", color="dark").pack(padx=16, pady=16)

tb.on_click(lambda: app.theme.use('dark'))
lt.on_click(lambda: b2.color('info'))


app.run()
