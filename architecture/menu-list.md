# Menu List

## List Options

**Properties**

- items: `dict[]`
- height: `int`
- width: `int`
- disabled: `bool`
- orientation: `Literal['horizontal', 'vertical']`
- display_expr: `str | Callable[[dict], str]` = text
- group_expr: `str | Callable[[dict], str]` = group
- on_item_clicked: `Callable`
- submenu_direction: 'str' = auto

## Menu Item

The menu item widget that includes three sections:
- Selection or Icon
- Text
- Shortcut of Chevron for a child menu

## Item Options

**Properties**

- selectable: `bool`
- selected: `bool`
- begin_group: `str`
- end_group: `str`
- items: `Item[]`
- disabled: `bool`
- underline: `int`
- selection_group: `str`
- text: `str`
- shortcut: `str`
- on_click: `str`

**Methods**

- update_data(data: `dict`)

# Standard List

A standard scrollable list component that includes search, grouping

**Properties** 

- items: `dict[]`
- height: `int`
- width: `int`
- grouped: `bool` False
- collapsible_groups: `bool` False
- row_factory: `Callable[[dict], Widget]`
- on_item_click: `Callable` = None
- on_item_deleted: `Callable` = None
- on_selection_changed: `Callable` = None
- selection_mode: `Literal['none', 'single', 'multiple']` = None
- selection_background: `str` = primary
- selection_controls_visible: `bool` = False
- scrollbar_visible: `bool` = True
- search_enabled: `bool` = False
- search_value: `str` = ''
- search_expr: `str | Callable[[dict], str]` = contains
- dragging_enabled: `bool` = False
- selected_items: `Item[]` = []
- display_expr: `str | Callable[[dict], str]` = text
