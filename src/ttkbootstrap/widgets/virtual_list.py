from typing import Any, Callable, Union

from ttkbootstrap.types import Primitive
from ttkbootstrap.widgets import Scrollbar
from ttkbootstrap.layouts import Pack
from ttkbootstrap.datasource.sqlite_source import DataSource
from ttkbootstrap.widgets.composites.list_item import ListItem
from ttkbootstrap.events import Event

VISIBLE_ROWS = 20
ROW_HEIGHT = 32


class VirtualList(Pack):
    def __init__(
            self,
            items: Union[DataSource, list[Primitive], list[ListItem], list[dict[str, Any]]] = None,
            row_factory: Callable=None,
            dragging_enabled = False,
            deleting_enabled = False,
            chevron_visible = False,
            scrollbar_visible = True,
            selection_background = 'primary',
            selection_mode = 'none',
            selection_controls_visible = False,
            **kwargs
    ):
        super().__init__(parent=kwargs.pop("parent", None), direction="horizontal")
        self._scrollbar_visible = scrollbar_visible

        self._options = dict(
            dragging_enabled = dragging_enabled,
            deleting_enabled = deleting_enabled,
            chevron_visible = chevron_visible,
            selection_background = selection_background,
            selection_mode = selection_mode,
            selection_controls_visible = selection_controls_visible
        )
        self._datasource = items if isinstance(items, DataSource) else DataSource().set_data(items or [])
        self._row_factory = row_factory or self._default_row_factory
        self._rows: list[ListItem] = []
        self._start_index = 0
        self._total_rows = self._datasource.total_count()


        # Layout
        self._canvas_frame = Pack(parent=self).attach(fill="both", expand=True)
        self._scrollbar = Scrollbar(parent=self, orient="vertical").attach(side="right", fill="y")
        if not self._scrollbar_visible:
            self._scrollbar.hide()

        self._canvas_frame.bind(Event.SELECTED, lambda x: self._on_select(x.data['id']))
        self._canvas_frame.bind(Event.DESELECTED, lambda x: self._on_deselected(x.data['id']))

        # Fixed row pool
        for _ in range(VISIBLE_ROWS):
            row = self._row_factory(self._canvas_frame, **self._options)
            row.widget.pack(fill="x")
            self._rows.append(row)

        # Scrollbar binding
        self._scrollbar.widget.config(command=self._on_scroll)
        self.bind_all(Event.MOUSE_WHEEL, self._on_mousewheel)
        self._update_rows()

    @classmethod
    def _default_row_factory(cls, parent, **kwargs):
        return ListItem(parent=parent, **kwargs)

    def _clamp_indices(self):
        # Always refresh counts before computing indices
        self._total_rows = self._datasource.total_count()
        # Max start index that still yields a full page (or 0 if dataset is small)
        max_start = max(0, self._total_rows - VISIBLE_ROWS)
        # Clamp to [0, max_start]
        if self._start_index < 0:
            self._start_index = 0
        elif self._start_index > max_start:
            self._start_index = max_start

    def _on_scroll(self, *args):
        # Keep counts fresh
        self._clamp_indices()
        if args[0] == "moveto":
            fraction = float(args[1])
            max_start = max(0, self._total_rows - VISIBLE_ROWS)
            self._start_index = int(round(fraction * max_start))
        elif args[0] == "scroll":
            steps = int(args[1])  # positive or negative
            self._start_index += steps
        # Final clamp, then paint
        self._clamp_indices()
        self._update_rows()

    def _on_mousewheel(self, event):
        # Windows: event.delta is ±120 multiples; macOS may be small increments
        step = -1 if event.delta > 0 else 1
        self._start_index += step
        self._clamp_indices()
        self._update_rows()

    def _update_rows(self):
        # Recompute counts and re-clamp every paint
        self._clamp_indices()

        page_data = self._datasource.get_page_from_index(self._start_index, VISIBLE_ROWS)

        for i, row in enumerate(self._rows):
            row.update_data(page_data[i] if i < len(page_data) else None)

        # Scrollbar thumb (guard small/empty datasets)
        denom = max(1, self._total_rows)  # avoid div/0
        first = (self._start_index / denom) if self._total_rows > 0 else 0.0
        last = ((self._start_index + VISIBLE_ROWS) / denom) if self._total_rows > 0 else 1.0
        last = min(last, 1.0)
        self._scrollbar.set(first, last)

    def _on_deselected(self, record_id):
        self._datasource.unselect_record(record_id)
        self._update_rows()

    def _on_select(self, record_id):
        if self._options.get('selection_mode') == 'single':
            self._datasource.unselect_all()
            self._datasource.select_record(record_id)
        else:
            self._datasource.select_record(record_id)
        self._update_rows()
