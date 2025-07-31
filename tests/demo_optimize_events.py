from ttkbootstrap.core import App
from ttkbootstrap.widgets import IconButton


app = App("Button Demo")

btn = IconButton(app, "moon-fill", variant="ghost").pack(side="left")

def toggle_theme():
    if app.theme.name == "light":
        app.theme.use('dark')
        btn.icon('sun-fill')
    else:
        app.theme.use('light')
        btn.icon('moon-fill')
    btn.process_idle_tasks()

btn.on_click(toggle_theme)
app.run()
