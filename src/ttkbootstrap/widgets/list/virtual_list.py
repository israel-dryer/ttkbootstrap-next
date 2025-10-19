from typing import Any, Callable, Literal, Union

from ttkbootstrap.datasource.memory_source import MemoryDataSource
from ttkbootstrap.datasource.types import DataSourceProtocol
from ttkbootstrap.events import Event
from ttkbootstrap.layouts import Pack
from ttkbootstrap.types import Primitive
from ttkbootstrap.widgets.list.list_item import ListItem
from ttkbootstrap.widgets.scrollbar import Scrollbar

VISIBLE_ROWS = 20
ROW_HEIGHT = 32


class VirtualList(Pack):
    def __init__(
            self,
            *,
            items: Union[DataSourceProtocol, list[Primitive], list[ListItem], list[dict[str, Any]]] = None,
            row_factory: Callable = None,
            dragging_enabled=False,
            deleting_enabled=False,
            chevron_visible=False,
            scrollbar_visible=True,
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
                dragging_enabled: Show a drag handle and emit a drag event.
                deleting_enabled: Show a delete button and emit a delete event.
                chevron_visible: Show a chevron icon.
                scrollbar_visible: Display a scrollbar when content overflows the list view.
                select_by_click: Select item by clicking the row; instead of only the selection control.
                selection_mode: Indicates what kind of selection is allowed on list items.
                selection_controls_visible: Show selection controls when selection is enabled.
                **kwargs: Additional keyword arguments.
        """
        super().__init__(parent=kwargs.pop("parent", None), direction="horizontal")
        self._scrollbar_visible = scrollbar_visible

        self._options = dict(
            dragging_enabled=dragging_enabled,
            deleting_enabled=deleting_enabled,
            chevron_visible=chevron_visible,
            selection_background=selection_background,
            select_by_click=select_by_click,
            selection_mode=selection_mode,
            selection_controls_visible=selection_controls_visible
        )
        self._datasource = items if isinstance(items, DataSourceProtocol) else MemoryDataSource().set_data(items or [])
        self._row_factory = row_factory or self._default_row_factory
        self._rows: list[ListItem] = []
        self._start_index = 0
        self._total_rows = self._datasource.total_count()

        # Layout
        self._canvas_frame = Pack(parent=self).attach(fill="both", expand=True)
        self._scrollbar = Scrollbar(parent=self, orient="vertical").attach(side="right", fill="y")
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
        for _ in range(VISIBLE_ROWS):
            row = self._row_factory(self._canvas_frame, **self._options)
            # keep your original packing approach
            row.widget.pack(fill="x")
            self._rows.append(row)

        # Scrollbar binding
        self._scrollbar.widget.config(command=self._on_scroll)
        self.on(Event.MOUSE_WHEEL, scope="all").listen(self._on_mousewheel)
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
        # Always refresh counts before computing indices
        self._total_rows = self._datasource.total_count()
        # Max start index that still yields a full page (or 0 if dataset is small)
        max_start = max(0, self._total_rows - VISIBLE_ROWS)
        # Clamp to [0, max_start]
        if self._start_index < 0:
            self._start_index = 0
        elif self._start_index > max_start:
            self._start_index = max_start

    # ----- Event handlers -----

    def _on_scroll(self, *args):
        # Keep counts fresh
        self._clamp_indices()
        if args and args[0] == "moveto":
            fraction = float(args[1])
            max_start = max(0, self._total_rows - VISIBLE_ROWS)
            self._start_index = int(round(fraction * max_start))
        elif args and args[0] == "scroll":
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

    # ----- Data ------

    def _update_rows(self):
        self._clamp_indices()
        page_data = self._datasource.get_page_from_index(self._start_index, VISIBLE_ROWS)

        for i, row in enumerate(self._rows):
            rec = page_data[i] if i < len(page_data) else None
            if rec is not None:
                # Compute the authoritative selection state
                rid = rec.get('id')
                if rid is not None and hasattr(self._datasource, 'is_selected'):
                    try:
                        sel = bool(self._datasource.is_selected(rid))
                    except Exception:
                        sel = bool(rec.get('selected', False))
                else:
                    sel = bool(rec.get('selected', False))

                # Inject selection into record so ListItem.update_data() handles it once
                rec = {**rec, 'selected': sel}

            row.update_data(rec)

        # Scrollbar thumb (guard small/empty datasets)
        denom = max(1, self._total_rows)  # avoid div/0
        first = (self._start_index / denom) if self._total_rows > 0 else 0.0
        last = ((self._start_index + VISIBLE_ROWS) / denom) if self._total_rows > 0 else 1.0
        last = min(last, 1.0)
        self._scrollbar.set(first, last)

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
