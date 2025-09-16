from ttkbootstrap import App, Pack, PasswordEntry

with App("Password Entry Demo", theme="dark") as app:
    with Pack(padding=16).layout(fill="both", expand=True):
        PasswordEntry(label="Password").show_visible_toggle(True)

app.run()
