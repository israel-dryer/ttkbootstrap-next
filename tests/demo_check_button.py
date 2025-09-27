from ttkbootstrap import App, Pack, Checkbutton

with App("Demo CheckButton", theme="dark") as app:
    with Pack(padding=16, gap=8, fill_items="x"):
        Checkbutton("Unchecked", 0, "danger")
        Checkbutton("Unchecked", 0, "success").on_invoke().listen(lambda _: print('toggled'))
        Checkbutton("Unchecked", 0).disable()
        cb = Checkbutton("Indeterminate", -1)
        cb.on_invoke().listen(lambda x: print(x))
        cb.on_changed().listen(lambda x: print(x))
        Checkbutton("Checked", 1)
        Checkbutton("Whatever")
app.run()
