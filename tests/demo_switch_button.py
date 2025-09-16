from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import SwitchButton

with App("Demo Switch Button") as app:
    with Pack(padding=16, fill_items="x", gap=16):
        SwitchButton("Air Conditioning", 0)
        SwitchButton("Water Softener", 1, color="danger")
        SwitchButton("Something Else")
app.run()
