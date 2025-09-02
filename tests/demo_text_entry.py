from ttkbootstrap.app import App
from ttkbootstrap.layouts import Grid
from ttkbootstrap.widgets import Button, Label, TextEntry

with App("Text Entry Demo", geometry="500x400") as app:
    with Grid(padding=16, columns=2, gap=8, sticky_items="ew").layout(fill="x"):
        TextEntry(label="First Name", required=True).layout(columnspan=2)
        TextEntry("16228 Kelby Cove", label="Address").layout(columnspan=2).readonly(True)
        occupation = TextEntry(label="Email", required=True).layout(columnspan=2)
        occupation.insert_addon(Label, text="@", position="left")
        Button("Submit").on_click(lambda: app.theme.use("dark"))
        Button("Cancel", variant="outline").on_click(lambda: app.theme.use("light"))
app.run()