from tkinter import Widget
from typing import Literal, TypedDict

SelectBy = Literal['index', 'key']


class ListItemOptions(TypedDict, total=False):
    """Configuration provided by parent container"""
    dragging_enabled: bool
    deleting_enabled: bool
    chevron_visible: bool
    select_by_click: bool
    selection_background: str
    selection_mode: Literal['single', 'multiple', 'none']
    selection_controls_visible: bool
    parent: Widget
