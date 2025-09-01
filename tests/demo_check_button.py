from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import CheckButton

with App("Demo CheckButton", theme="dark") as app:
    with Pack(padding=16, gap=8, fill_items="x"):
        CheckButton("Unchecked", 0, "danger")
        CheckButton("Unchecked", 0, "success")
        CheckButton("Unchecked", 0).disable()
        CheckButton("Indeterminate", -1, on_toggle=lambda: print('Clicked'))
        CheckButton("Checked", 1, on_change=lambda x: print(x))
app.run()
