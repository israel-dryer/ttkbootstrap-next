from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets.entry.variants.date import DateEntry

with App("Demo Date Entry") as app:
    with Pack(padding=16, gap=8):
        DateEntry("March 14, 1981", "Birthdate", message="Required").add_validation_rule(
            "required", message="This is required")
        DateEntry()
app.run()
