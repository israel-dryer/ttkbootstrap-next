from ttkbootstrap_next.app import App
from ttkbootstrap_next.layouts import Pack
from ttkbootstrap_next.widgets.list.virtual_list import VirtualList

with App("Simple List Demo") as app:
    with Pack().attach(fill='both', expand=True):
        data = [f"Item {x}" for x in range(500)]
        VirtualList(items=data).attach(fill="both", expand=True)
app.run()
