from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets.parts.number_spinner_part import NumberSpinnerPart

with App() as app:
    with Pack():
        NumberSpinnerPart()
        NumberSpinnerPart()

app.run()