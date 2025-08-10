from ttkbootstrap import App
from ttkbootstrap.widgets import Button
from ttkbootstrap.layouts.flexbox import FlexBox

with App("Flexbox Column Grow", theme="dark") as app:
    app.geometry("600x400")

    with FlexBox(
            direction="row", justify_content="stretch", align_content="center",
            sticky="nsew", expand=True, gap=12, padding=12):
        Button(text="A", weight=2)  # 2 parts width
        Button(text="B")  # 1 part (default)
        Button(text="C", weight=0)  # no horizontal expansion

    with FlexBox(direction="column", justify_content="stretch", align_content="center",
                 sticky="nsew", expand=True, gap=12, padding=12):
        Button(text="Top",    weight=2)  # 2 parts height
        Button(text="Middle", weight=1)  # 1 part
        Button(text="Bottom", weight=0)  # no vertical expansion


app.run()
