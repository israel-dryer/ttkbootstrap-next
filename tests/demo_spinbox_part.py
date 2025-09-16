from ttkbootstrap import App, Pack
from ttkbootstrap.widgets.entry.shared.spinbox_part import SpinboxPart

with App() as app:
    with Pack():
        SpinboxPart()
        SpinboxPart()

app.run()
