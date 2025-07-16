from ttkbootstrap.core import App
from ttkbootstrap.widgets import CheckButton, Frame, IconButton, LabelFrame, RadioButton
from ttkbootstrap.widgets.button import Button

app = App("Button Demo")

b1 = Button(app, "Primary", color="primary", icon="house-fill").pack(padx=16, pady=16)
b2 = Button(app, "Secondary", color="secondary", icon="house-fill", variant="ghost").pack(padx=16, pady=16)
f1 = LabelFrame(app, border_color="primary-subtle", padding=8).pack(padx=10, pady=10, fill='x')
i1 = IconButton(f1, "moon-fill", variant="ghost").pack(side="left")
IconButton(f1, "badge-hd-fill", variant="ghost").pack(side="left")
IconButton(f1, "bag-check-fill", variant="ghost").pack(side="left")
CheckButton(f1, "Is Deployed").pack(padx=10, pady=10)
#
f3 = Frame(app, padding=16).pack()
RadioButton(app, "Red", color="danger", value="red", group="colors", on_change=lambda x: print(x)).pack(side="left")
RadioButton(app, "Blue", value="blue", group="colors", selected=True).pack(side="left")
RadioButton(app, "Green", color="success", value="green", group="colors").pack(side="left")


def toggle_theme():
    if app.theme.name == "light":
        app.theme.use('dark')
        i1.icon('sun-fill')
    else:
        app.theme.use('light')
        i1.icon('moon-fill')


i1.on_click(toggle_theme)

app.run()
