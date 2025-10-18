from ttkbootstrap import App, Pack, Button, VirtualList
from ttkbootstrap.datasource import MemoryDataSource

# TODO create a label variant for list-radio and list-checkbox to enable faster state selection changes
records = [{"id": i, "text": f"Item {i}", "caption": "Caption", "icon": "apple"} for i in range(100)]

with App("Demo Virtual Listbox", geometry="500x500", theme="dark") as app:

    ds = MemoryDataSource(page_size=25)
    ds.set_data(records)

    Button("Dark", command=lambda: app.theme.use("dark")).attach()
    Button("Light", command=lambda: app.theme.use("light")).attach()

    with Pack().attach(fill='both', expand=True):
        vl = VirtualList(
            items=ds,
            dragging_enabled=True,
            deleting_enabled=True,
            selection_mode="single",
            selection_controls_visible=True,
            select_by_click=True,
        ).attach(fill="both", expand=True)

        vl.on_item_deleted().listen(lambda x: print(x))
        vl.on_item_click().listen(lambda x: print(x))

app.run()

# with App("Demo Virtual Listbox", geometry="500x500", theme="dark") as app:
#
#     Button("Dark", command=lambda: app.theme.use("dark")).attach()
#     Button("Light", command=lambda: app.theme.use("light")).attach()
#
#     with Pack().attach(fill='both', expand=True):
#         vl = VirtualList(
#             items=["one", "two", "three"],
#             dragging_enabled=True,
#             deleting_enabled=True,
#             selection_mode="multiple",
#             selection_controls_visible=True,
#         ).attach(fill="both", expand=True)
#
#         vl.on_selection_changed().listen(lambda x: print(x))
#
# app.run()
