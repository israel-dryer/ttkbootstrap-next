from ttkbootstrap.core import App
from ttkbootstrap.widgets import Frame, Separator
from ttkbootstrap.widgets.parts.list_item_part import ListItemPart

app = App(theme="dark")

frame = Frame(app).pack(fill='both', expand=True)

for x in range(5):

    ListItemPart(
        frame,
        key=str(x),
        icon='house-fill',
        # title='title',
        # badge='35',
        select_background="secondary",
        caption='small text here',
        text="Hello World",
        selection=dict(mode="multiple"),
        show_chevron=True,
        allow_deleting=True,
        allow_reordering=True
    ).pack(fill='x')
    Separator(frame).pack(fill='x')

frame.bind('selected', lambda s: print(s))
frame.bind('deselected', lambda d: print(d))
frame.bind('deleted', lambda v: print(v))

    # ListItemPart(
    #     frame,
    #     # icon='house-fill',
    #     # title="Title",
    #     selection_mode="multiple",
    #     selection_group="my-stuff",
    #     badge=dict(text="6", variant="circle"),
    #     # show_chevron=True,
    #     allow_deleting=True,
    #     allow_reordering=True,
    #     text=f"Item {x}",
    #     # memo="something small to say",
    # ).pack(fill='x')

app.run()
