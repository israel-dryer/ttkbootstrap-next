# Flexbox Layout Design

The flexbox will use a `Frame` widget with a `grid` geometry manager.

The flexbox will support `direction` of:
- row: `side="left"`
- row-reverse: `side="right"`
- column: `side="top"`
- column-reverse: `side="bottom"`

To support alignment, justification, and gap, there will be spacer columns or rows between each item.

Gap will be added by giving a minimum width or height (depending direction) to each spacer that is equal to the gap. This will be on each spacer except the first and last.

The following `justify_content` and `align_content` options will be supported:
- space-between: All spacers have `weight = 1` except the first and last.
- space-around: All spacers have `weight = 1`
- stretch: All spacers have `weight = 0`; all other columns/rows (depending on direction) have `weight = 1`
- start: All spacers have `weight = 0` except the last.
- end: All spacers have a `weight = 0` except the first.
- center: First and last spacers have `weight = 1`, all others `weight = 0`.

`justify_self`, `justify_items`, `align_self`, and `align_items` will support "stretch", "center", "start", "end" and will be adjusted with the `sticky` option.

"justify" will always refer to the horizontal axis while "align" will always refer to the "vertical" axis.
