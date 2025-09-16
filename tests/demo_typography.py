from ttkbootstrap.app import App
from ttkbootstrap.layouts.pack import Pack
from ttkbootstrap.style.typography import Typography
from ttkbootstrap.widgets import Label

with App("Typography Demo") as app:
    with Pack(padding=16, gap=16, direction="column"):
        for token in Typography.all()._fields:
            Label(text=token.replace("_", " ").title(), font=token.replace('_', '-'))

app.run()
