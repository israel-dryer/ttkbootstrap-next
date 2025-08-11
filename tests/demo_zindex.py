from ttkbootstrap import App
from ttkbootstrap.layouts.gridbox import GridBox
from ttkbootstrap.widgets import Button


def bump_z(btn):
    current = btn.zindex() or 0
    btn.zindex(current + 1)
    print(current)

with App(geometry="800x800") as app:

    with GridBox(padding=16, gap=16, rows=1, columns=1):
        b5 = Button(text="Button 5", row=1, column=1)
        b6 = Button(text="Button 6", on_click=lambda: bump_z(b6), zindex=10, row=1, column=1)
        b7 = Button(text="Button 7", on_click=lambda: bump_z(b7), zindex=12, row=1, column=1)
        b8 = Button(text="Button 8", on_click=lambda: bump_z(b8), row=1, column=1)

        print("b5:", b5.zindex(), "b6:", b6.zindex(), "b7:", b7.zindex(), "b8:", b8.zindex())

app.run()