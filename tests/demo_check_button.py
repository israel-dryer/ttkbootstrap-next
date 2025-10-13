from ttkbootstrap import App, Checkbutton, Pack

with App("Demo CheckButton", theme="dark") as app:
    with Pack(padding=16, gap=8, fill_items="x").attach(padx=10, pady=10):
        Checkbutton("Unchecked", 0, color="danger").attach()
        Checkbutton("Unchecked", 0, color="success").attach().on_invoke().listen(lambda _: print('toggled'))
        Checkbutton("Unchecked", 0).attach().disable()
        cb = Checkbutton("Indeterminate", -1).attach()
        cb.on_invoke().listen(lambda x: print(x))
        cb.on_changed().listen(lambda x: print(x))
        Checkbutton("Checked", 1).attach()
        Checkbutton("Whatever").attach()
app.run()
