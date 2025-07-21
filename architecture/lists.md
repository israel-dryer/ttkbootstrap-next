# Dev Extreme Inspired List

This is a general purpose list widget with obviously a lot of options. Using all of them makes no sense in real life,
but they all should be available to use if needed.

In addition to these dev extreme features, I'm going to add a title and memo field. To make the api as flexible as
possible, for a lot of options I'm going to allow the user to pass in a string or object. If the item is an object, then
it will be assumed as configuration properties passed to the item. Otherwise, it will be interpreted directly as text,
or something else that is typically expected. This is required to allow some customization that is not available in a
non-web environment. Also, I'm going to allow for a slot for the menu shortcut commands. Not sure exactly how this will
be formatted, but I'll thing of something.

## Overall structure

`[checkbox] [icon] [text] [badge] [chevron] [delete] [drag]`

The delete button rolls into the context menu when a context menu is created. Otherwise it shows up on the widget.

## List Properties

- allow_reordering: `bool`: Whether to allow item dragging.
- allow_item_deleting `bool`: Whether or not user can delete items.
- alternating_row_color `string`: The background color of alternating rows.
- data `Union[str, Object]`: A collection of strings or objects.
- disabled `bool`: Whether the list responds to user interaction.
- display_field `str`: The field name of the object to display as `text`.
- takes_focus `bool`: Whether or not list can accept focus during keyboard traversal.
- height `int`: The height of the widget in pixels.
- hover_state_enabled `bool`: Whether to show visual indication of hover states.
- items `Union[str, Object]`: A list of strings or objects.
- key `str`: The id of the data; each must be unique.
- menu_items `{text: str, icon: str, command: Callable}`: Configuration for a right-click context menu.
- on_item_click `callable`: Function called when the item is clicked.
- on_item_deleted `callable`: Function called when item is deleted.
- on_selection_changed `callable`: Function called after selection changes.
- search_enabled `bool`: Whether search panel is visible.
- search_expr `string[]`: An array of field names to search.
- search_mode `contains, startswith, equals`: The operation used to perform search.
- search_value `string`: The search string.
- select_all_mode `page, all`: How items are selected.
- select_by_click `bool`: whether item is selected if clicked by user.
- selected_item_keys `string[]` An array of selected item ids
- selected_items `string[], object[]`: An array of selected items.
- selection_mode `Literal[multiple, single, none]`: How data is selected.
- show_scrollbar `Literal[hover, scroll]`: When to show the scrollbar.
- show_separator `bool`: Whether to show the list item separator.
- show_selection_controls `bool`: Whether to display selection controls when selection is enabled.
- width `int`: The widget of the widget in pixels.

## List Methods

- delete_item(index)
- focus()
- get_data()
- is_item_selected(value, by="index") `[index, key]`
- configure(option=None, **kwargs)
- reload()
- scroll_to(value, by="index") `[index, key, location]`
- scroll_to_top()
- select_all()
- select_item(value, by="index") `[index, key]`
- unselect_all()
- unselect_item(value, by="index") `[index, key]`

## Item Properties

- badge `str`: The text of a badge displayed for the list item
- disabled `bool`: Whether the item responds to user interaction
- icon `str`: The name of the icon to display.
- text `str: dict`: The text to display on the item.
- title `str : dict`: The item header text.
- memo `str : dict`: The dimmed text displayed below the item text.
- show_chevron `bool`: Whether or not to display a chevron for this item.
- item_dragging `object`: Settings for item dragging.


## Active and Hover States

A list should support active and hover states. This means updating the underlying style of all of the child widgets
in the list item to react to these various states.

The hover state should be a light variation