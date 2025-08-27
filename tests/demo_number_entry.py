from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import NumberEntry

with App("Number Entry Demo") as app:
    with Pack(padding=16, gap=8, fill_items="x"):
        NumberEntry(25, "Age", "How much is there left?", show_spin_buttons=False)
        NumberEntry(label="Time Remaining")

app.run()
