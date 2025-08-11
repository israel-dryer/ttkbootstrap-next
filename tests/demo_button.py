from ttkbootstrap import App

from ttkbootstrap.widgets import Button, IconButton
from ttkbootstrap.layouts.flexgrid import FlexGrid

with App("Button Demo", theme="dark", geometry="800x600") as app:
    with FlexGrid(padding=16, gap=16):
        with FlexGrid(columns=3, padding=16, sticky_items="new", sticky="new", expand=True, surface="background-1"):
            Button(text="Fixed Placement - Up", color="success", position="fixed").place(x=0, y=0, width="100%")
            Button(text="Fixed Placement - Dw", color="success", position="fixed").place(x=0, y="100%", width="100%", anchor="sw")
            b3 = Button(text="Button 2", color="secondary")
            print('zindex', b3.zindex())
            Button(text="Button 3", color="secondary")
            Button(text="Button 4", color="secondary", offset=1)
            Button(text="Button 5", color="secondary", colspan=3)


        with FlexGrid(rows=1, padding=8, sticky="w"):
            IconButton(icon="house-fill", color="secondary")
            IconButton(icon="gear-fill", color="warning")
            IconButton(icon="trash-fill", color="danger")

        with FlexGrid(rows=1, sticky="new", expand=True, gap=16, padding=16, surface="background-3", height=200,
                propagate=False):
            Button(text="Button 1", color="secondary", sticky="nw")
            Button(text="Button 2", color="secondary", sticky="news")
            Button(text="Button 3", color="secondary", sticky="se")

        with FlexGrid(columns=3, rows=1, sticky="new", expand=True, padding=16):
            Button(text="Left", sticky="w")
            Button(text="Right", offset=1, sticky="e")

app.run()
