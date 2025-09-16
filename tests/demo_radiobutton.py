from ttkbootstrap import App, Pack, Label, Radiobutton

with App() as app:
    with Pack(fill_items="x", gap=8, padding=16):
        Label("Radio Button Demo", font="heading-md")
        Radiobutton("One", 1, group="number")
        Radiobutton("Two", 2, color="danger", group="number")
        Radiobutton("Three", 3, group="number").on_selected(lambda x: print(x)).on_deselected(
            lambda x: print(x)).on_invoke(lambda x: print(x))
app.run()
