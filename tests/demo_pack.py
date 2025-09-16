from ttkbootstrap import App, Pack, Button

with App("Pack Demo", geometry="500x500") as app:
    with Pack(padding=8, gap=8, fill_items="x").layout(fill="x"):
        for x in range(10):
            Button("Button")

app.run()
