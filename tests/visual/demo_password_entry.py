from ttkbootstrap_next import App, Pack, PasswordEntry

with App("Password Entry Demo", theme="dark") as app:
    with Pack(padding=16).attach(fill="both", expand=True):
        PasswordEntry(label="Password").attach().show_visible_toggle(True)

app.run()
