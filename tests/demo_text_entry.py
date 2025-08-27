from ttkbootstrap.app import App
from ttkbootstrap.layouts import Grid
from ttkbootstrap.widgets import Button, Label, TextEntry

with App("Text Entry Demo", geometry="500x500") as app:
    with Grid(padding=16, columns=2, gap=8, sticky_items="ew").layout(fill="x"):
        TextEntry("Israel", label="First Name").layout(columnspan=2)
        TextEntry(label="Address").layout(columnspan=2)
        occupation = TextEntry(message="This is required").layout(columnspan=2)
        occupation.insert_addon(Label, text="@", position="left")
        Button("Submit")
        Button("Cancel", variant="outline")
app.run()