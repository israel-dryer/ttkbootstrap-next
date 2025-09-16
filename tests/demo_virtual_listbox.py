from ttkbootstrap import App, Pack, Button, VirtualList
from ttkbootstrap.datasource import DataSource

with App("Demo Virtual Listbox", geometry="500x500", theme="dark") as app:
    records = [{"id": i, "text": f"Item {i}", "caption": "Caption", "icon": "house-fill"} for i in range(500)]

    ds = DataSource(page_size=25)
    ds.set_data(records)

    Button("Dark", on_invoke=lambda: app.theme.use("dark"))
    Button("Light", on_invoke=lambda: app.theme.use("light"))

    with Pack().layout(fill='both', expand=True):
        VirtualList(
            items=ds,
            selection_mode="multiple",
            chevron_visible=True,
            selection_controls_visible=True,
            dragging_enabled=True,
            deleting_enabled=True,
        ).layout(fill="both", expand=True)

app.run()
