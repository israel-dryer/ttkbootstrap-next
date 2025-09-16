from ttkbootstrap import App, NumericEntry, Pack

with App("Number Entry Demo") as app:
    with Pack(padding=16, gap=8, fill_items="x"):
        ne = NumericEntry(0.25, "Age", "How much is there left?", show_spin_buttons=False, increment=1.0)
        ne.on_enter(lambda x: print(x))
        ne.on_input(lambda x: print("Changed", x))
        ne.on_changed(lambda x: print("Change", x))
        NumericEntry(value=0, label="Time Remaining")

app.run()
