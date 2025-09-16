from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import PasswordEntry

with App("Password Entry Demo", theme="dark") as app:
    with Pack(padding=16).layout(fill="both", expand=True):
        PasswordEntry(label="Password").show_visible_toggle(True)

app.run()
