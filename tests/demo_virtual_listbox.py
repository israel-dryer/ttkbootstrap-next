from ttkbootstrap import App, Pack, Button, VirtualList
from ttkbootstrap.datasource import DataSource

with App("Demo Virtual Listbox", geometry="500x500", theme="dark") as app:
    records = [{"id": i, "text": f"Item {i}", "caption": "Caption", "icon": "house-fill"} for i in range(50)]

    ds = DataSource(page_size=25)
    ds.set_data(records)

    Button("Dark", command=lambda: app.theme.use("dark"))
    Button("Light", command=lambda: app.theme.use("light"))

    with Pack().attach(fill='both', expand=True):
        VirtualList(
            items=ds,
            selection_mode="single",
            chevron_visible=True,
            selection_controls_visible=True,
            dragging_enabled=True,
            deleting_enabled=True,
        ).attach(fill="both", expand=True)

app.run()
