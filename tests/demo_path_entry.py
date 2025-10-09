from ttkbootstrap import App, Pack, PathEntry, TextEntry

with App("Demo File Entry") as app:
    with Pack(padding=16, fill_items="x").layout(fill="x"):
        PathEntry().on_changed().listen(lambda x: te.value(x.data['value']))
        te = TextEntry()
app.run()
