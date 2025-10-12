from ttkbootstrap import App, Pack, Button

with App("Demo Place", geometry="400x400") as app:
    with Pack().attach(fill="both", expand=True):
        Button("Absolute").attach("place", x=100, y=100)
app.run()
