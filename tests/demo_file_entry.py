from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import FileEntry, TextEntry

with App("Demo File Entry") as app:
    with Pack(padding=16, fill_items="x").layout(fill="x"):
        FileEntry(on_changed=lambda x: print(x))
        TextEntry()
app.run()