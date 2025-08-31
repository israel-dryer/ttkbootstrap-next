from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Button, Notebook

# Context Manager Version
with App("Notebook Demo", geometry="500x500") as app:
    with Pack(padding=16).layout(fill='both', expand=True):
        with Notebook().layout(fill='both', expand=True) as nb:
            with nb.Pack("Tab 1", name="tab1"):
                Button('Tab 1 - Option 1', on_click=lambda: nb.select('tab2'))
                Button('Tab 1 - Option 2')

            with nb.Grid("Tab 2", name="tab2"):
                Button('Tab 2 - Option 1', on_click=lambda: nb.select('tab1'))
                Button('Tab 2 - Option 2')

app.run()


# Inline Version
# app = App()
#
# container = Pack(parent=app, padding=16).attach(fill='both', expand=True)
# notebook = Notebook(parent=container).attach(fill='both', expand=True)
#
# tab1 = notebook.Pack("Tab 1", name="tab1", parent=notebook)
# Button("Tab 1 - Option1 ", on_click=lambda: notebook.select('tab2'), parent=tab1).attach()
# Button("Tab 1 - Option 1", parent=tab1).attach()
# notebook.add(tab1)
#
# tab2 = notebook.Pack("Tab 2", name="tab2", parent=notebook)
# Button("Tab 2 - Option1 ", on_click=lambda: notebook.select('tab1'), parent=tab2).attach()
# Button("Tab 2 - Option 1", parent=tab2).attach()
# notebook.add(tab2)
#
# app.run()
