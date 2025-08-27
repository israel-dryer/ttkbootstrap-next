from ttkbootstrap.app import App
from ttkbootstrap.datasource.sqlite_source import DataSource
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.virtual_list import VirtualList

with App("Demo Virtual Listbox", geometry="500x500", theme="dark") as app:
    records = [{"id": i, "text": f"Item {i}", "caption": "Caption", "icon": "house-fill"} for i in range(500)]

    ds = DataSource(page_size=25)
    ds.set_data(records)

    Button("Dark", on_click=lambda: app.theme.use("dark"))
    Button("Light", on_click=lambda: app.theme.use("light"))

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