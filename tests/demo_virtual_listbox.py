import sys

sys.path.insert(0, r'D:\Development\ttkbootstrap\src')

from ttkbootstrap import App, VirtualList
from ttkbootstrap.layouts import Pack
from ttkbootstrap.datasource import MemoryDataSource

records = [
    {"id": 1, "text": "Alabama", "caption": "Montgomery", "icon": "pin-map"},
    {"id": 2, "text": "Alaska", "caption": "Juneau", "icon": "pin-map"},
    {"id": 3, "text": "Arizona", "caption": "Phoenix", "icon": "pin-map"},
    {"id": 4, "text": "Arkansas", "caption": "Little Rock", "icon": "pin-map"},
    {"id": 5, "text": "California", "caption": "Sacramento", "icon": "pin-map"},
    {"id": 6, "text": "Colorado", "caption": "Denver", "icon": "pin-map"},
    {"id": 7, "text": "Connecticut", "caption": "Hartford", "icon": "pin-map"},
    {"id": 8, "text": "Delaware", "caption": "Dover", "icon": "pin-map"},
    {"id": 9, "text": "Florida", "caption": "Tallahassee", "icon": "pin-map"},
    {"id": 10, "text": "Georgia", "caption": "Atlanta", "icon": "pin-map"},
    {"id": 11, "text": "Hawaii", "caption": "Honolulu", "icon": "pin-map"},
    {"id": 12, "text": "Idaho", "caption": "Boise", "icon": "pin-map"},
    {"id": 13, "text": "Illinois", "caption": "Springfield", "icon": "pin-map"},
    {"id": 14, "text": "Indiana", "caption": "Indianapolis", "icon": "pin-map"},
    {"id": 15, "text": "Iowa", "caption": "Des Moines", "icon": "pin-map"},
    {"id": 16, "text": "Kansas", "caption": "Topeka", "icon": "pin-map"},
    {"id": 17, "text": "Kentucky", "caption": "Frankfort", "icon": "pin-map"},
    {"id": 18, "text": "Louisiana", "caption": "Baton Rouge", "icon": "pin-map"},
    {"id": 19, "text": "Maine", "caption": "Augusta", "icon": "pin-map"},
    {"id": 20, "text": "Maryland", "caption": "Annapolis", "icon": "pin-map"},
    {"id": 21, "text": "Massachusetts", "caption": "Boston", "icon": "pin-map"},
    {"id": 22, "text": "Michigan", "caption": "Lansing", "icon": "pin-map"},
    {"id": 23, "text": "Minnesota", "caption": "Saint Paul", "icon": "pin-map"},
    {"id": 24, "text": "Mississippi", "caption": "Jackson", "icon": "pin-map"},
    {"id": 25, "text": "Missouri", "caption": "Jefferson City", "icon": "pin-map"},
    {"id": 26, "text": "Montana", "caption": "Helena", "icon": "pin-map"},
    {"id": 27, "text": "Nebraska", "caption": "Lincoln", "icon": "pin-map"},
    {"id": 28, "text": "Nevada", "caption": "Carson City", "icon": "pin-map"},
    {"id": 29, "text": "New Hampshire", "caption": "Concord", "icon": "pin-map"},
    {"id": 30, "text": "New Jersey", "caption": "Trenton", "icon": "pin-map"},
    {"id": 31, "text": "New Mexico", "caption": "Santa Fe", "icon": "pin-map"},
    {"id": 32, "text": "New York", "caption": "Albany", "icon": "pin-map"},
    {"id": 33, "text": "North Carolina", "caption": "Raleigh", "icon": "pin-map"},
    {"id": 34, "text": "North Dakota", "caption": "Bismarck", "icon": "pin-map"},
    {"id": 35, "text": "Ohio", "caption": "Columbus", "icon": "pin-map"},
    {"id": 36, "text": "Oklahoma", "caption": "Oklahoma City", "icon": "pin-map"},
    {"id": 37, "text": "Oregon", "caption": "Salem", "icon": "pin-map"},
    {"id": 38, "text": "Pennsylvania", "caption": "Harrisburg", "icon": "pin-map"},
    {"id": 39, "text": "Rhode Island", "caption": "Providence", "icon": "pin-map"},
    {"id": 40, "text": "South Carolina", "caption": "Columbia", "icon": "pin-map"},
    {"id": 41, "text": "South Dakota", "caption": "Pierre", "icon": "pin-map"},
    {"id": 42, "text": "Tennessee", "caption": "Nashville", "icon": "pin-map"},
    {"id": 43, "text": "Texas", "caption": "Austin", "icon": "pin-map"},
    {"id": 44, "text": "Utah", "caption": "Salt Lake City", "icon": "pin-map"},
    {"id": 45, "text": "Vermont", "caption": "Montpelier", "icon": "pin-map"},
    {"id": 46, "text": "Virginia", "caption": "Richmond", "icon": "pin-map"},
    {"id": 47, "text": "Washington", "caption": "Olympia", "icon": "pin-map"},
    {"id": 48, "text": "West Virginia", "caption": "Charleston", "icon": "pin-map"},
    {"id": 49, "text": "Wisconsin", "caption": "Madison", "icon": "pin-map"},
    {"id": 50, "text": "Wyoming", "caption": "Cheyenne", "icon": "pin-map"}
]

with App("Demo Virtual Listbox", geometry="500x500", theme="dark") as app:
    ds = MemoryDataSource(page_size=25)
    ds.set_data(records)

    with Pack(padding=2).attach(fill='both', expand=True):
        vl = VirtualList(
            items=ds,
            show_separators=True,
            search_enabled=True,
            search_expr=['text', 'caption'],
            selection_mode="single",
            selection_controls_visible=False,
            select_by_click=True,
        ).attach(fill="both", expand=True)

        vl.on_item_deleting().cancel_when(lambda ev: ev.data['id'] == 105).listen(lambda e: print(e))
        vl.on_item_deleted().listen(lambda x: print(x))
        # vl.on_item_click().listen(lambda x: print(x))
        # vl.on_item_selected().listen(lambda x: print(x))

        # Optional: listen to drag events
        # vl.on_item_reordered().listen(lambda e: print(f"✓ Reordered: {e.data['from_index']} → {e.data['to_index']}"))
        # vl.on_item_reorder_failed().listen(lambda e: print(f"✗ Reorder failed: {e.data}"))

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
