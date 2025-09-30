from ttkbootstrap import App, Pack, Sizegrip

with App("Sizegrip Demo", geometry="400x400") as app:
    with Pack(surface="danger", padding=16).layout(fill='both', expand=True):
        Sizegrip().layout(side="bottom", anchor="e")

app.run()
