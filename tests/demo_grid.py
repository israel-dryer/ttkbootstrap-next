from ttkbootstrap import App, Grid, Button

with App("Demo Grid Layout") as app:
    with Grid(rows=[0, 1, 0], columns=[0, 1, 0], padding=8, gap=8).layout(fill='both', expand=True):
        for x in range(4):
            Button(text="Button", icon="house-fill").layout(sticky="nsew")
            Button(icon="house-fill", variant="outline").layout(sticky="")
app.run()
