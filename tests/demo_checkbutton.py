from ttkbootstrap import App
from ttkbootstrap.layouts.flexgrid import FlexGrid
from ttkbootstrap.widgets import CheckButton

with App("Demo Checkbutton", theme="dark") as app:
    with FlexGrid(gap=8, padding=8, sticky_items="ew"):
        CheckButton(text="Unchecked", color="success", value=0)
        CheckButton(text="Unchecked", color="success", value=0)
        CheckButton(text="Unchecked", value=0)
        CheckButton(text="Indeterminate", value=-1, on_toggle=lambda: print('Clicked')).disable()
        CheckButton(text="Checked", value=1, on_change=lambda x: print(x))

app.run()
