from ttkbootstrap.app import App
from ttkbootstrap.layouts.flexgrid import FlexGrid
from ttkbootstrap.widgets._parts.entry_part import EntryPart

with App() as app:
    with FlexGrid(gap=8, padding=8):
        EntryPart().on_changed(lambda x: print('changed', x)).add_validation_rule('required').on_validated(
            lambda x: print(x))
        EntryPart()

app.run()
