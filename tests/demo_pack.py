from ttkbootstrap import App, Button, Pack

with App("Pack Demo", geometry="500x500") as app:
    with Pack(padding=8, fill_items="x").attach(fill="x"):
        for x in range(10):
            Button("Button").attach()

app.run()
