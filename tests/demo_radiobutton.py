from ttkbootstrap_next import App, Label, Pack, Radiobutton

with App() as app:
    with Pack(fill_items="x", gap=8, padding=16).attach():
        Label("Radio Button Demo", font="heading-md").attach()
        Radiobutton("One", 1, group="number").attach()
        Radiobutton("Two", 2, color="danger", group="number").attach()
        rb = Radiobutton("Three", 3, group="number").attach()
        rb.on_selected().listen(lambda x: print(x))
        rb.on_deselected().listen(lambda x: print(x))
app.run()
