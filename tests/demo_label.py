from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Label

with App("Label Demo") as app:
    with Pack(padding=16):
        Label("Hello world", icon="house-fill", icon_position="end", anchor="center", font="body-xl")

app.run()