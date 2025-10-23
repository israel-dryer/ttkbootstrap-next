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


** Some other ideas and thoughts **


menu_items = [

    {"text": "File", "items": [
    
        {"type": "button", "text": "New", "key": "new", "accel": "Ctrl+N"},
        {"type": "button", "text": "Open", "key": "open", "accel": "Ctrl+O"},
        {"type": "button", "text": "Save As", "key": "saveas", "accel": "Ctrl+S"},
        {"type": "separator"},
        {"type": "button", "text": "Exit", "key": "exit", "accel": "Alt+F4"},
    ]},
    {"text": "Edit", "items": [
    ...
    ]}
]


with Menu() as m:
    with Menu.Cascade("File")
        Menu.Button("New", key="new", accel="Ctrl+N")
        Menu.Button("Open", key="open", accel="Ctrl+O")
        Menu.Button("Save As", key="saveas", accel="Ctrl+S")
        Menu.Separator()
        Menu.Button("Exit", key="exit", accel="Alt+F4")
    with Menu.Cascade("Edit")
        Menu.Button("Undo", key="undo")
        Menu.Button("Redo", key="redo")
        Menu.Separator()
        Menu.Button("Cut", key="cut", accel="Ctrl+X")
        Menu.Button("Copy", key="copy", accel="Ctrl+C")
        Menu.Separator()
        Menu.Toggle("Show space and tab", key="space_tab", selected=False)
    with Menu.Cascade("Encoding")
        Menu.Radio("ANSI", key="encode_ansi", value=0, selected=True)
        Menu.Radio("UTF-8", key="encode_utf_8", value=1)
        Menu.Radio("UTF-16-BOM", key="encode_utf_16_bom", value=2)
        Menu.Separator()
   
    m.on_menu_item_click().listen(lambda e: handle_menu_item_click(e))

        
def handle_menu_item_click(event):
    match event.data['key']:
        case "new":
            ...
        case "open":
            ...
        case "saveas":
            ...
        case "exit":
            ...
        case "cut":
            ...
        case _:
            ...
