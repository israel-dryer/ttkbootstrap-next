from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets.virtual_list import VirtualList

with App("Simple List Demo") as app:
    with Pack().layout(fill='both', expand=True):
        data = [f"Item {x}" for x in range(500)]
        VirtualList(items=data).layout(fill="both", expand=True)
app.run()
