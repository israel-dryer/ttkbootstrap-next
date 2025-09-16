from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Checkbutton

with App("Demo CheckButton", theme="dark") as app:
    with Pack(padding=16, gap=8, fill_items="x"):
        Checkbutton("Unchecked", 0, "danger")
        Checkbutton("Unchecked", 0, "success").on_invoke(lambda: print('toggled'))
        Checkbutton("Unchecked", 0).disable()
        Checkbutton("Indeterminate", -1).on_invoke(lambda x: print(x)).on_changed(lambda x: print(x))
        Checkbutton("Checked", 1, on_changed=lambda x: print(x))
        Checkbutton("Whatever", on_invoke=lambda: print("Hello"))
app.run()
