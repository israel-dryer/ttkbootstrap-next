from typing import Callable, Union

from ttkbootstrap.widgets import Frame, Label, Scrollbar
from ttkbootstrap.core.datasource import DataSource
from ttkbootstrap.widgets.parts import ListItemPart

VISIBLE_ROWS = 20
ROW_HEIGHT = 32


class VirtualList(Frame):
    def __init__(
            self,
            parent,
            items: Union[list[dict], DataSource],
            row_factory: Callable=None,
            dragging_enabled = False,
            deleting_enabled = False,
            chevron_visible = False,
            scrollbar_visible = True,
            selection_background = 'primary',
            selection_mode = 'none',
            selection_controls_visible = False
    ):
        super().__init__(parent)
        self._scrollbar_visible = scrollbar_visible
        self.grid_column_configure(0, weight=1)
        self.grid_row_configure(0, weight=1)

        self._options = dict(
            dragging_enabled = dragging_enabled,
            deleting_enabled = deleting_enabled,
            chevron_visible = chevron_visible,
            selection_background = selection_background,
            selection_mode = selection_mode,
            selection_controls_visible = selection_controls_visible
        )
        self._datasource = items if isinstance(items, DataSource) else DataSource().set_data(items)
        self._row_factory = row_factory or self._default_row_factory
        self._rows: list[ListItemPart] = []
        self._start_index = 0
        self._total_rows = items.total_count()


        # Layout
        self._canvas_frame = Frame(self).grid(row=0, column=0, sticky='nsew')
        self._scrollbar = Scrollbar(self, orient="vertical")
        if self._scrollbar_visible:
            self._scrollbar.grid(row=0, column=1, sticky="ns")
        self._canvas_frame.bind('select', lambda x: self._on_select(x.data['id']))
        self._canvas_frame.bind('unselect', lambda x: self._on_deselected(x.data['id']))

        # Fixed row pool
        for _ in range(VISIBLE_ROWS):
            row = self._row_factory(self._canvas_frame, **self._options)
            row.widget.pack(fill="x")
            self._rows.append(row)

        # Scrollbar binding
        self._scrollbar.widget.config(command=self._on_scroll)
        self.bind_all("mouse-wheel", self._on_mousewheel)
        self._update_rows()

    @classmethod
    def _default_row_factory(cls, parent, **kwargs):
        return ListItemPart(parent, **kwargs)

    def _on_resize(self, event):
        width = event.width
        for row in self._rows:
            row.configure(width=width)

    def _on_scroll(self, *args):
        if args[0] == "moveto":
            fraction = float(args[1])
            self._start_index = int(fraction * (self._total_rows - VISIBLE_ROWS))
        elif args[0] == "scroll":
            direction = int(args[1])
            self._start_index = max(0, min(self._start_index + direction, self._total_rows - VISIBLE_ROWS))
        self._update_rows()

    def _on_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        self._start_index = max(0, min(self._start_index + delta, self._total_rows - VISIBLE_ROWS))
        self._update_rows()

    def _update_rows(self):
        page_data = self._datasource.get_page_from_index(self._start_index, VISIBLE_ROWS)
        for i, row in enumerate(self._rows):
            if i < len(page_data):
                row.update_data(page_data[i])
            else:
                row.update_data(None)

        first = self._start_index / self._total_rows
        last = min((self._start_index + VISIBLE_ROWS) / self._total_rows, 1.0)
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
