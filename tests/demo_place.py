from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Button

with App("Demo Place", geometry="400x400") as app:
    with Pack().layout(fill="both", expand=True):
        Button("Absolute", position="absolute").layout(x=100, y=100)
app.run()