from ttkbootstrap.core import App
from ttkbootstrap.style.style import Style
from ttkbootstrap.widgets import CheckButton, Frame, IconButton, Notebook
from ttkbootstrap.widgets.buttons.button import Button

app = App("Button Demo", surface="layer-4")
style = Style()

theme = app.theme

b1 = Button(app, "Primary", color="primary", icon="house-fill", take_focus=False).pack(padx=16, pady=16)
b2 = Button(app, "Secondary", color="secondary", icon="house-fill", variant="ghost").pack(padx=16, pady=16)
nb = Notebook(app).pack()

nb.add(f1 := Frame(nb), 'Tab 1')
nb.add(f2 := Frame(nb), 'Tab 2')
nb.add(f3 := Frame(nb), 'Tab 3')

i1 = IconButton(f1, "moon-fill", variant="ghost").pack(side="left")
IconButton(f1, "badge-hd-fill", variant="ghost").pack(side="left")
IconButton(f1, "bag-check-fill", variant="ghost").pack(side="left")
CheckButton(f1, "Is Deployed").pack(padx=10, pady=10)


def toggle_theme():
    if app.theme.name == "light":
        app.theme.use('dark')
        i1.icon('sun-fill')
    else:
        app.theme.use('light')
        i1.icon('moon-fill')


i1.on_click(toggle_theme)

app.run()

