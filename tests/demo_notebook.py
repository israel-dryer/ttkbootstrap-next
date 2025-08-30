from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Button, Notebook

with App() as app:

    with Pack(padding=16).layout(fill='both', expand=True):

        with Notebook().layout(fill='both', expand=True) as nb:

            with Pack(surface="blue-200", padding=16, gap=16) as tab1:
                Button('Tab 1 - Option 1', on_click=lambda: nb.select('tab2'))
                Button('Tab 1 - Option 2')
                nb.add(tab1, name="tab1", text="Tab 1", sticky="nsew")

            with Pack(surface="red-200", padding=16, gap=16) as tab2:
                Button('Tab 2 - Option 1', on_click=lambda: nb.select('tab1'))
                Button('Tab 2 - Option 2')
                nb.add(tab2, name="tab2", text='Tab 2', sticky="nsew")

app.run()