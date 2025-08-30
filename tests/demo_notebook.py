from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack, Notebook
from ttkbootstrap.widgets import Button

# Context Manager Version
with App("Notebook Demo") as app:

    with Pack(padding=16).layout(fill='both', expand=True):

        with Notebook().layout(fill='both', expand=True) as nb:

            with Pack(surface="blue-200", padding=16, gap=16).layout(name="tab1", text="Tab 1") as tab1:
                Button('Tab 1 - Option 1', on_click=lambda: nb.select('tab2'))
                Button('Tab 1 - Option 2')


            with Pack(surface="red-200", padding=16, gap=16).layout(name="tab2", text="Tab 2") as tab2:
                Button('Tab 2 - Option 1', on_click=lambda: nb.select('tab1'))
                Button('Tab 2 - Option 2')

app.run()

"""
# Inline Version
app = App()

container = Pack(parent=app, padding=16).attach(fill='both', expand=True)
notebook = Notebook(parent=container).attach(fill='both', expand=True)

tab1 = Pack(parent=notebook, surface='blue-200', padding=16, gap=16)
Button("Tab 1 - Option1 ", on_click=lambda: notebook.select('tab2'), parent=tab1).attach()
Button("Tab 1 - Option 1", on_click=lambda: notebook.select('tab2'), parent=tab1).attach()
notebook.add(tab1, name="tab1", text="Tab 1")

tab2 = Pack(parent=notebook, surface='red-200', padding=16, gap=16)
Button("Tab 2 - Option1 ", on_click=lambda: notebook.select('tab1'), parent=tab2).attach()
Button("Tab 2 - Option 1", on_click=lambda: notebook.select('tab1'), parent=tab2).attach()
notebook.add(tab2, name="tab2", text="Tab 2")

app.run()
"""