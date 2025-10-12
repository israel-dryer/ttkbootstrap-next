from ttkbootstrap import App, Pack, PathEntry, TextEntry

with App("Demo File Entry") as app:
    with Pack(padding=16, fill_items="x").attach(fill="x"):
        PathEntry().attach().on_changed().listen(lambda x: te.value(x.data['value']))
        te = TextEntry().attach()
app.run()
