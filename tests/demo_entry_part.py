from ttkbootstrap_next.app import App
from ttkbootstrap_next.layouts import Grid
from ttkbootstrap_next.widgets.entry.shared.entry_mixin import EntryMixin
from ttkbootstrap_next.widgets.entry.shared.entry_part import EntryPart
from ttkbootstrap_next.widgets.mixins.composite_mixin import CompositeWidgetMixin


class TestEntry(CompositeWidgetMixin, EntryMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._entry = EntryPart()


with App() as app:
    with Grid(gap=8, padding=8).layout(fill="x"):
        TestEntry()

app.run()
