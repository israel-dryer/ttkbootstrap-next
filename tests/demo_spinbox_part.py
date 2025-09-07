from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets.parts.number_spinner_part import SpinboxPart

with App() as app:
    with Pack():
        SpinboxPart()
        SpinboxPart()

app.run()