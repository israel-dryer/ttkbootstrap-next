from ttkbootstrap import App, Pack, Button, VirtualList
from ttkbootstrap.datasource import DataSource

# TODO create a label variant for list-radio and list-checkbox to enable faster state selection changes

with App("Demo Virtual Listbox", geometry="500x500", theme="dark") as app:
    records = [{"id": i, "text": f"Item {i}", "caption": "Caption", "icon": "apple"} for i in range(100)]

    ds = DataSource(page_size=25)
    ds.set_data(records)

    Button("Dark", command=lambda: app.theme.use("dark")).attach()
    Button("Light", command=lambda: app.theme.use("light")).attach()

    with Pack().attach(fill='both', expand=True):
        VirtualList(
            items=ds,
            dragging_enabled=True,
            deleting_enabled=True,
            selection_mode="multiple",
            selection_controls_visible=True,
        ).attach(fill="both", expand=True)

app.run()
