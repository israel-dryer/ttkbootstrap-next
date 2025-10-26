from ttkbootstrap_next import App, Pack, Button, Progressbar

with App("Demo Progressbar") as app:
    with Pack(padding=16, gap=8, fill_items="x").attach(fill="x"):
        pb1 = Progressbar(50).attach()
        pb1.on_complete().listen(lambda x: print(x))
        pb2 = Progressbar(60, variant="striped").attach()
        Button("Step", command=lambda: pb1.step()).attach()
        Button("Start", command=lambda: pb2.start()).attach()
        Button("In State", command=lambda: print(pb2.widget.state())).attach()
app.run()
