from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Button

with App("Demo Button") as app:
    with Pack(padding=16).layout(fill="x"):
        Button(icon="house-fill")
        Button("House", icon="house")
        Button("House", icon="house-fill")
        Button("House", icon="house-fill", color="warning")
        Button(icon="house", variant="outline")
        Button(icon="house", variant="ghost", color="dark", on_click=lambda: app.theme.use('light'))
        Button("House", icon="house", variant="outline", on_click=lambda: app.theme.use('dark'))
app.run()
