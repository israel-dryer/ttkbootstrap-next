from ttkbootstrap.app import App
from ttkbootstrap.layouts import Grid
from ttkbootstrap.widgets.parts.entry_part import EntryPart

with App() as app:
    with Grid(gap=8, padding=8).layout(fill="x"):
        (
            EntryPart()
            .on_changed(lambda x: print('Changed', x))
            .add_validation_rule('required')
            .on_validated(lambda x: print('Validation rule', x))
        )
        EntryPart()

app.run()
