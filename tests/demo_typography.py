from ttkbootstrap_next import App, Label
from ttkbootstrap_next.style import Typography

with App("Typography Demo") as app:
    for token in Typography.all()._fields:
        Label(text=token.replace("_", " ").title(), font=token.replace('_', '-')).attach()

app.run()
