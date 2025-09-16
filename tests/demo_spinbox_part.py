from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets.entry.parts import SpinboxPart

with App() as app:
    with Pack():
        SpinboxPart()
        SpinboxPart()

app.run()