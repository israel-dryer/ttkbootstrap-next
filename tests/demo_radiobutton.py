from ttkbootstrap import App, Label, Pack, Radiobutton

with App() as app:
    with Pack(fill_items="x", gap=8, padding=16):
        Label("Radio Button Demo", font="heading-md")
        Radiobutton("One", 1, group="number")
        Radiobutton("Two", 2, color="danger", group="number")
        rb = Radiobutton("Three", 3, group="number")
        rb.on_selected().listen(lambda x: print(x))
        rb.on_deselected().listen(lambda x: print(x))
app.run()
