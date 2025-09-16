from ttkbootstrap import App, Pack, Button, Progressbar

with App("Demo Progressbar") as app:
    with Pack(padding=16, gap=8, fill_items="x").layout(fill="x"):
        # Progressbar(75).start(4)
        pb = Progressbar(50).on_complete(lambda x: print(x)).on_changed(lambda x: print(x))
        # Progressbar(60).start(7)
        Button("Step", on_invoke=lambda: pb.step())
app.run()
