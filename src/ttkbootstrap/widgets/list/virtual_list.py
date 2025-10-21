from typing import Any, Callable, Literal, Union

from ttkbootstrap.datasource.memory_source import MemoryDataSource
from ttkbootstrap.datasource.types import DataSourceProtocol
from ttkbootstrap.events import Event
from ttkbootstrap.layouts import Pack
from ttkbootstrap.types import Primitive
from ttkbootstrap.widgets.entry import TextEntry
from ttkbootstrap.widgets.label import Label
from ttkbootstrap.widgets.list.list_item import ListItem
from ttkbootstrap.widgets.scrollbar import Scrollbar

VISIBLE_ROWS = 20
ROW_HEIGHT = 32
OVERSCAN_ROWS = 2  # small buffer for smoother scroll/resizes
EMPTY = {"__empty__": True, "id": "__empty__"}


class VirtualList(Pack):
    def __init__(
            self,
            *,
            items: Union[DataSourceProtocol, list[Primitive], list[ListItem], list[dict[str, Any]]] = None,
            row_factory: Callable = None,
            dragging_enabled=False,
            deleting_enabled=False,
            chevron_visible=False,
            row_alternation_enabled=False,
            row_alternation_color="background-1",
            row_alternation_mode: Literal['even', 'odd'] = "even",
            scrollbar_visible=True,
            show_separators=True,
            search_enabled=False,
            search_expr: list[str] = None,
            search_mode: Literal["contains", "startswith", "endswidth", "equals"] = "contains",
            selection_background: str = 'primary',
            select_by_click: bool = False,
            selection_mode: Literal['single', 'multiple', 'none'] = 'none',
            selection_controls_visible=False,
            **kwargs
    ):
        """
            Initialize a virtual list.

            Keyword Arguments:
                items: A list of items used to populate the list.
                row_factory: A factory function used to generate the list items.
                row_alternation_enabled: Display alternating rows a different color.
                row_alternation_color: The color of the alternating rows (default, surface-2)
                row_alternation_mode: Whether to alternate even or odd rows.
                dragging_enabled: Show a drag handle and emit a drag event.
                deleting_enabled: Show a delete button and emit a delete event.
                chevron_visible: Show a chevron icon.
                scrollbar_visible: Display a scrollbar when content overflows the list view.
                search_enabled: Display a search entry above the list.
                search_expr: The field(s) to use when executing the search query.
                search_mode: The search method to execute.
                show_separators: Display a separator between list items..
                select_by_click: Select item by clicking the row; instead of only the selection control.
                selection_mode: Indicates what kind of selection is allowed on list items.
                selection_controls_visible: Show selection controls when selection is enabled.
                **kwargs: Additional keyword arguments.
        """
        super().__init__(parent=kwargs.pop("parent", None), direction="vertical", fill_items='x')
        self._scrollbar_visible = scrollbar_visible

        self._options = dict(
            dragging_enabled=dragging_enabled,
            deleting_enabled=deleting_enabled,
            chevron_visible=chevron_visible,
            show_separators=show_separators,
            selection_background=selection_background,
            select_by_click=select_by_click,
            selection_mode=selection_mode,
            selection_controls_visible=selection_controls_visible,
            row_alternation_enabled=row_alternation_enabled,
            row_alternation_color=row_alternation_color,
            row_alternation_mode=row_alternation_mode,
        )
        self._datasource = items if isinstance(items, DataSourceProtocol) else MemoryDataSource().set_data(items or [])
        self._row_factory = row_factory or self._default_row_factory
        self._rows: list[ListItem] = []
        self._start_index = 0
        self._total_rows = self._datasource.total_count()
        self._visible_rows = VISIBLE_ROWS
        self._row_height = ROW_HEIGHT
        self._page_size = VISIBLE_ROWS + OVERSCAN_ROWS
        self._focused_record_id = None  # Track which record has logical focus

        # Search
        self._search_enabled = search_enabled
        self._search_expr = search_expr
        self._search_mode = search_mode
        if self._search_enabled and self._search_expr:
            self._search_entry = TextEntry(parent=self, show_messages=False)
            self._search_entry.insert_addon(Label, icon="search", position="left")
            self._search_entry.on_input().listen(self._on_search_text)
            self._search_entry.attach()

        # List layout
        self._canvas_frame = Pack(parent=self).attach(fill="both", expand=True)
        self._canvas_frame.on(Event.CONFIGURE).listen(self._on_resize)
        self._scrollbar = Scrollbar(parent=self, orient="vertical").attach("place", x="100%", height="100%", xoffset=4)
        if not self._scrollbar_visible:
            self._scrollbar.hide()

        # Event streams - persist and expose to enable cancellable events
        self._deleting_stream = self._hub.on(Event.ITEM_DELETING)
        self._deleting_stream.listen(self._on_deleting)

        self._inserting_stream = self._hub.on(Event.ITEM_INSERTING)
        self._inserting_stream.listen(self._on_inserting)

        self._updating_stream = self._hub.on(Event.ITEM_UPDATING)
        self._updating_stream.listen(self._on_updating)

        self._selecting_stream = self._hub.on(Event.ITEM_SELECTING)
        self._selecting_stream.listen(self._on_selecting)

        self._deselecting_stream = self._hub.on(Event.ITEM_DESELECTING)
        self._deselecting_stream.listen(self._on_deselecting)

        # Fixed row pool
        self._ensure_row_pool(self._page_size)
        self.schedule.after(0, self._remeasure_and_relayout)

        # Scrollbar binding
        self._scrollbar.widget.config(command=self._on_scroll)
        self.on(Event.MOUSE_WHEEL, scope="all").listen(self._on_mousewheel)

        # Listen for focus events from list items
        self._hub.on(Event.ITEM_FOCUSED).listen(self._on_item_focused)

        self._update_rows()

    # ----- Helpers -----

    @property
    def _hub(self):
        """Convenience alias used for emitting events on this object"""

        return self._canvas_frame

    @classmethod
    def _default_row_factory(cls, parent, **kwargs):
        return ListItem(parent=parent, **kwargs)

    def _clamp_indices(self):
        self._total_rows = self._datasource.total_count()
        vr = max(1, self._visible_rows)
        max_start = max(0, self._total_rows - vr)
        if self._start_index < 0:
            self._start_index = 0
        elif self._start_index > max_start:
            self._start_index = max_start

    # ----- Event handlers -----

    def _on_search_text(self, event):
        search_term = event.data['text']
        query_parts = []
        for key in self._search_expr:
            match self._search_mode:
                case "startswith":
                    query_parts.append(f"{key} LIKE '{search_term}%'")
                case "endswidth":
                    query_parts.append(f"{key} LIKE '%{search_term}'")
                case "equals":
                    query_parts.append(f"{key} = '{search_term}'")
                case _:
                    query_parts.append(f"{key} LIKE '%{search_term}%'")

        where_sql = " OR ".join(query_parts).strip()
        self._datasource.set_filter(where_sql)
        self._update_rows()

    def _on_scroll(self, *args):
        self._clamp_indices()
        if args and args[0] == "moveto":
            fraction = float(args[1])
            max_start = max(0, self._total_rows - max(1, self._visible_rows))
            self._start_index = int(round(fraction * max_start))
        elif args and args[0] == "scroll":
            number = int(args[1])
            what = args[2] if len(args) > 2 else "units"
            step = self._visible_rows if what == "pages" else 1
            self._start_index += number * step
        self._clamp_indices()
        self._update_rows()

    def _on_mousewheel(self, event):
        step = -1 if event.delta > 0 else 1
        self._start_index += step
        self._clamp_indices()
        self._update_rows()

    def _on_deselecting(self, event: Any):
        self._datasource.unselect_record(event.data['id'])
        self._update_rows()
        selected = self._datasource.get_selected()
        self._hub.emit(Event.ITEM_DESELECTED, data=event.data)
        self._hub.emit(Event.CHANGED, selected=selected)

    def _on_selecting(self, event: Any):
        if self._options.get('selection_mode') == 'single':
            self._datasource.unselect_all()
            self._datasource.select_record(event.data['id'])
        else:
            self._datasource.select_record(event.data['id'])
        self._update_rows()
        selected = self._datasource.get_selected()
        self._hub.emit(Event.ITEM_SELECTED, data=event.data)
        self._hub.emit(Event.SELECTION_CHANGED, selected=selected)

    def _on_deleting(self, event: Any):
        try:
            self._datasource.delete_record(event.data['id'])
            self._update_rows()
            self._hub.emit(Event.ITEM_DELETED, data=event.data)
        except Exception as error:
            self._hub.emit(Event.ITEM_DELETE_FAILED, data={**event.data, "reason": error.args[0]})

    def _on_inserting(self, event: Any):
        try:
            record = event.data
            record_id = self._datasource.create_record(record)
            record['id'] = record_id
            self._update_rows()
            self._hub.emit(Event.ITEM_INSERTED, data=record)
        except Exception as error:
            self._hub.emit(Event.ITEM_INSERT_FAILED, data={**event.data, "reason": error.args[0]})

    def _on_updating(self, event: Any):
        try:
            updated = self._datasource.update_record(event.data['id'], event.data.updates)
            if updated:
                self._update_rows()
                self._hub.emit(Event.ITEM_UPDATED, data=event.data)
            else:
                self._hub.emit(
                    Event.ITEM_UPDATE_FAILED, data={**event.data, "reason": "Datasource rejected the update."})
        except Exception as error:
            self._hub.emit(Event.ITEM_UPDATE_FAILED, data={**event.data, "reason": error.args[0]})

    def _on_item_focused(self, event: Any):
        """Handle when a list item receives focus - track which record is focused."""
        record_id = event.data.get('id')
        if record_id and record_id != '__empty__':
            self._focused_record_id = record_id
            # Force update to apply focused state to the correct row
            self._update_rows()

    # ----- Helpers ------

    def _update_rows(self):
        self._clamp_indices()
        page_data = self._datasource.get_page_from_index(self._start_index, self._page_size)

        for i, row in enumerate(self._rows):
            rec = page_data[i] if i < len(page_data) else EMPTY
            # if ListItem ever gets pack_forget/destroyed elsewhere, make sure it's packed:
            if not row.widget.winfo_manager():
                row.widget.pack(fill="x")
            # preserve selection and focus flags
            if rec is not EMPTY:
                rid = rec.get('id')
                if rid is not None and hasattr(self._datasource, 'is_selected'):
                    try:
                        sel = bool(self._datasource.is_selected(rid))
                    except Exception:
                        sel = bool(rec.get('selected', False))
                else:
                    sel = bool(rec.get('selected', False))

                # Check if this record should have logical focus
                focused = (rid is not None and rid == self._focused_record_id)

                rec = {**rec, 'selected': sel, 'focused': focused, "item_index": i + self._start_index}
            row.update_data(rec)

        total = max(1, self._total_rows)
        first = (self._start_index / total) if self._total_rows > 0 else 0.0
        last = ((self._start_index + max(1, self._visible_rows)) / total) if self._total_rows > 0 else 1.0
        if last < first:
            last = first
        self._scrollbar.set(first, min(last, 1.0))

    def _compute_sizes(self) -> tuple[int, int]:
        try:
            h = int(self._canvas_frame.widget.winfo_height())
        except Exception:
            h = 0

        # Use the measured row height; guard against zero
        rh = max(1, int(self._row_height) or ROW_HEIGHT)

        visible = max(1, (h // rh) if h > 0 else self._visible_rows or VISIBLE_ROWS)
        page = visible + OVERSCAN_ROWS
        # Also cap by total rows so clamping math can reach the end exactly
        total = max(0, self._datasource.total_count())
        visible = min(visible, total) if total else visible
        page = min(page, total) if total else page
        return visible, page

    def _on_resize(self, *_):
        self._remeasure_and_relayout()

    def _compute_page_size(self) -> int:
        """Return how many rows fit in the viewport, with a small overscan."""
        try:
            h = int(self._canvas_frame.widget.winfo_height())
        except Exception:
            h = 0

        # If height not yet laid out, fall back to previous or default
        base = max(1, (h // self._row_height) if h > 0 else self._page_size or VISIBLE_ROWS)
        return base + OVERSCAN_ROWS

    def _ensure_row_pool(self, needed: int):
        """Grow/shrink the pooled ListItem widgets to match the needed page size."""
        # Grow
        while len(self._rows) < needed:
            row = self._row_factory(self._canvas_frame, **self._options)
            row.widget.pack(fill="x")
            self._rows.append(row)
        # Shrink
        while len(self._rows) > needed:
            row = self._rows.pop()
            row.destroy()

    def _remeasure_and_relayout(self):
        """Measure real row height, then recompute visible/page sizes and repaint."""
        if not self._rows:
            return
        # Measure actual widget height; fall back to requested if 0 (not yet mapped)
        rh = self._rows[0].widget.winfo_height()
        if rh <= 1:
            rh = self._rows[0].widget.winfo_reqheight()

        # If ListItem adds internal padding/margins, this captures it.
        if rh and rh != self._row_height:
            self._row_height = rh

        # Recompute sizes with the true row height
        vis, page = self._compute_sizes()
        size_changed = (vis != self._visible_rows) or (page != self._page_size)

        # Always ensure pool >= page and repaint when height changed
        self._visible_rows, self._page_size = vis, page
        self._ensure_row_pool(self._page_size)
        self._clamp_indices()
        self._update_rows()

    # ----- Event streams -----

    def on_item_selecting(self):
        """Convenience alias for item selecting stream"""
        return self._selecting_stream

    def on_item_selected(self):
        """Convenience alias for item selected stream"""
        return self._hub.on(Event.ITEM_SELECTED)

    def on_selection_changed(self):
        """Convenience alias for selection changed stream"""
        return self._hub.on(Event.SELECTION_CHANGED)

    def on_item_deselecting(self):
        """Convenience alias for item deselecting stream"""
        return self._deselecting_stream

    def on_item_deselected(self):
        """Convenience alias for item deselected stream"""
        return self._hub.on(Event.ITEM_DESELECTED)

    def on_item_deleting(self):
        """Convenience alias for item deleting stream"""
        return self._deleting_stream

    def on_item_deleted(self):
        """Convenience alias for item deleted stream"""
        return self._hub.on(Event.ITEM_DELETED)

    def on_item_delete_failed(self):
        """Convenience alias for item delete failed stream"""
        return self._hub.on(Event.ITEM_DELETE_FAILED)

    def on_item_click(self):
        """Convenience alias for the item click stream"""
        return self._hub.on(Event.ITEM_CLICK)

    def on_item_inserting(self):
        """Convenience alias for item inserting stream"""
        return self._inserting_stream

    def on_item_inserted(self):
        """Convenience alias for item inserted stream"""
        return self._hub.on(Event.ITEM_INSERTED)

    def on_item_insert_failed(self):
        """Convenience alias for item insert failed stream"""
        return self._hub.on(Event.ITEM_INSERT_FAILED)

    def on_item_updating(self):
        """Convenience alias for item updating stream"""
        return self._updating_stream

    def on_item_updated(self):
        """Convenience alias for item updated stream"""
        return self._hub.on(Event.ITEM_UPDATED)

    def on_item_update_failed(self):
        """Convenience alias for item update failed stream"""
        return self._hub.on(Event.ITEM_UPDATE_FAILED)

    # ----- Actions -----

    def reload(self):
        """Reload from datasource and redraw the rows"""
        self._datasource.reload()
        self._update_rows()

    # ----- Mutators -----

    def delete_item(self, key: str):
        """Delete item by key"""
        self._hub.emit(Event.ITEM_DELETING, data={'id': key})

    def insert_item(self, value: dict):
        """Insert new item"""
        self._hub.emit(Event.ITEM_INSERTING, data=value)

    def update_item(self, key: str, changes: dict):
        """Update item by key"""
        self._hub.emit(Event.ITEM_UPDATING, data={"id": key, "changes": changes})

    # ----- Query -----

    def get_item(self, key: str):
        return self._datasource.read_record(key)

    def get_items(self, keys: list[str]):
        return list(map(self._datasource.read_record, keys))

    # ----- Selection -----

    def select_item(self, key: str):
        """Select item by key"""
        self._hub.emit(Event.ITEM_SELECTING, data={"id": key})

    def deselect_item(self, key: str):
        """Deselect item by key"""
        self._hub.emit(Event.ITEM_DESELECTING, data={"id": key})

    def unselect_all(self):
        """Unselect all items"""
        self._datasource.unselect_all()
        self._update_rows()
        selected = self._datasource.get_selected()
        self._hub.emit(Event.CHANGED, selected=selected)
