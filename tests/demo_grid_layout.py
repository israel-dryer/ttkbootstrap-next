from ttkbootstrap import App
from ttkbootstrap.layouts.flexgrid import FlexGrid
from ttkbootstrap.widgets import Button

with App(geometry="800x800") as app:

    with FlexGrid(sticky_items="new", padding=8):
        for x in range(5):
            Button(text=f"Button-{x}")

app.run()