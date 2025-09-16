from ttkbootstrap.app import App
from ttkbootstrap.layouts import Grid
from ttkbootstrap.widgets.entry.shared.entry_mixin import EntryMixin
from ttkbootstrap.widgets.entry.shared.entry_part import EntryPart
from ttkbootstrap.widgets.mixins.composite_mixin import CompositeWidgetMixin


class TestEntry(CompositeWidgetMixin, EntryMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._entry = EntryPart()


with App() as app:
    with Grid(gap=8, padding=8).layout(fill="x"):
        TestEntry()

app.run()
