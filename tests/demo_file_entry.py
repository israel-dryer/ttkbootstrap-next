from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import FileEntry

with App("Demo File Entry") as app:
    with Pack(padding=16, fill_items="x").layout(fill="x"):
        FileEntry()
app.run()