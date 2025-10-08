from ttkbootstrap import App, Pack, Button, Progressbar

with App("Demo Progressbar") as app:
    with Pack(padding=16, gap=8, fill_items="x").layout(fill="x"):
        pb1 = Progressbar(50)
        pb1.on_complete().listen(lambda x: print(x))
        pb2 = Progressbar(60)
        Button("Step", command=lambda: pb1.step())
        Button("Start", command=lambda: pb2.start())
        Button("In State", command=lambda: print(pb2.widget.state()))
app.run()
