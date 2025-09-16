from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import NumericEntry

with App("Number Entry Demo") as app:
    with Pack(padding=16, gap=8, fill_items="x"):
        ne = NumericEntry(0.25, "Age", "How much is there left?", show_spin_buttons=False)
        ne.on_enter(lambda x: print(x))
        #ne.on_input(lambda x: print("Changed", x))
        ne.on_changed(lambda x: print("Change", x))
        NumericEntry(label="Time Remaining")

app.run()
