from ttkbootstrap.core import App
from ttkbootstrap.core.datasource import DataSource
from ttkbootstrap.widgets import Label, Button
from ttkbootstrap.widgets.data.virtual_list import VirtualList
from ttkbootstrap.widgets.parts import ListItemPart
from ttkbootstrap.widgets.parts.simple_list_item_part import SimpleListItemPart

if __name__ == "__main__":
    app = App(title="Virtual List", theme="light")
    app.geometry('500x500')

    records = [{"id": i, "text": f"Item {i}", "caption": "Caption"} for i in range(500)]
    ds = DataSource(page_size=25)
    ds.set_data(records)

    # data {icon, title, text, caption}
    # dragging_enabled
    # deleting_enabled
    # chevron_visible
    # selection_background
    # selection_mode
    # selection_controls_visible

    vl = VirtualList(
        app,
        items=ds,
        selection_mode='multiple',
        chevron_visible=True,
        selection_controls_visible=True
    )
    vl.pack(fill="both", expand=True)

    app.run()
