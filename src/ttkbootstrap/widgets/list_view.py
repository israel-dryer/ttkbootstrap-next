from typing import Literal

from ttkbootstrap.datasource.sqlite_source import DataSource
from ttkbootstrap.widgets import Frame

SelectBy = Literal['index', 'key']

class ListBox(Frame):

    def __init__(
            self,
            parent,
            items: list[dict],
            *,
            allow_reordering=False,
            allow_deleting=False,
            alternate_row_color: str = None,
            menu_items: list[dict] = None,
            search_enabled=False,
            search_expr: list[str] = None,
            search_mode: Literal["contains", "startswith", "equals"],
            search_value: str = None,
            selection_mode: Literal["none", "single", "multiple"] = "none",
            page_size: int = 10,
            show_scrollbar=False,
            show_separator=False,
            width: int = None,
            **kwargs
    ):
        self._datasource = DataSource()
        self._datasource.set_data(items)

        self._selected_items = []
        super().__init__(parent)

    # event handlers

    def on_item_click(self):
        pass

    def on_item_deleted(self):
        pass

    def on_selection_changed(self):
        pass

    # data handling

    def reload(self):
        pass

    def delete_item(self, key: str):
        pass

    def insert_item(self, value: dict):
        pass

    def update_item(self, key: str, data: dict):
        pass

    def get_item(self, key: str):
        pass

    def get_items(self):
        pass

    # scrolling

    def scroll_to(self, key: str):
        pass

    def scroll_to_top(self):
        pass

    def reload(self):
        pass

    # pagination

    def next_page(self):
        pass

    def prev_page(self):
        pass

    # search

    def search_items(self, term: str):
        pass

    def clear_search(self):
        pass

    # item selection

    def select_item(self, key: str):
        pass

    def unselect_item(self, key: str):
        pass

    def select_all(self):
        pass

    def unselected_all(self):
        pass

    def is_item_selected(self, key: str):
        pass
