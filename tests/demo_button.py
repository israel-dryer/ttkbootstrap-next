from tkinter import ttk

from ttkbootstrap.core import App
from ttkbootstrap.widgets import IconButton
from ttkbootstrap.widgets.button import Button

app = App("Button Demo", surface="base")

b1 = Button(app, "Primary", color="primary", icon="house-fill").pack(padx=16, pady=16).disable()
b2 = Button(app, "Primary", color="primary", icon="house-fill").pack(padx=16, pady=16)
Button(app, "Primary", color="primary").pack(padx=16, pady=16)
Button(app, "Secondary", color="secondary", size="lg", icon="house-fill").pack(padx=16, pady=16)
Button(app, "Success", color="success", size="sm", icon="chevron-right", icon_position="right").pack(padx=16, pady=16)
Button(app, "Warning", color="warning").pack(padx=16, pady=16)
Button(app, "Danger", color="danger").pack(padx=16, pady=16)
IconButton(app, "house-fill", color="secondary").pack(padx=10)
IconButton(app, "bar-chart-fill", color="light", size="sm").pack(padx=10)
IconButton(app, "basket3-fill", color="info", size="lg").pack(padx=10)
ac = Button(app, "Accent Bg", color="info").pack(padx=16, pady=16)
lt = Button(app, "Light", color="light", size="sm").pack(padx=16, pady=16)
tb = Button(app, "Dark", color="dark").pack(padx=16, pady=16)


tb.on_click(lambda: app.theme.use('dark'))
lt.on_click(lambda: app.theme.use('light'))

app.run()
