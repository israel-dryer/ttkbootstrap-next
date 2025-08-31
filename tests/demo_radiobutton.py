from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Label
from ttkbootstrap.widgets.radio_button import RadioButton

with App() as app:
    with Pack(fill_items="x", gap=8, padding=16):
        Label("Radio Button Demo", font="heading-md")
        RadioButton("One", 1, "Numbers", selected=True)
        RadioButton("Two", 2, "Numbers", color="danger")
        RadioButton("Three", 3, "Numbers")
app.run()