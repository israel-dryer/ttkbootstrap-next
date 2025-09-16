from ttkbootstrap import App, Pack, PathEntry, TextEntry

with App("Demo File Entry") as app:
    with Pack(padding=16, fill_items="x").layout(fill="x"):
        PathEntry(on_changed=lambda x: print(x))
        TextEntry()
app.run()
