from ttkbootstrap.core import App
from ttkbootstrap.widgets import IconButton, Separator
from ttkbootstrap.widgets.button import Button
from ttkbootstrap.widgets.frame import Frame

app = App("Button Demo")

b1 = Button(app, "Primary", color="primary", icon="house-fill").pack(padx=16, pady=16)
b2 = Button(app, "Secondary", color="secondary", icon="house-fill", variant="ghost").pack(padx=16, pady=16)

f1 = Frame(app, padding=8, surface="warning-subtle").pack(padx=10, pady=10, fill='x')
i1 = IconButton(f1, "moon-fill", variant="ghost").pack(side="left")
IconButton(f1, "badge-hd-fill", variant="ghost").pack(side="left")
IconButton(f1, "bag-check-fill", variant="ghost").pack(side="left")

Separator(app).pack(pady=16, padx=16, fill='x')


def toggle_theme():
    if app.theme.name == "light":
        app.theme.use('dark')
        i1.icon('sun-fill')
    else:
        app.theme.use('light')
        i1.icon('moon-fill')


i1.on_click(toggle_theme)

app.run()
