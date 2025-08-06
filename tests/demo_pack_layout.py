from ttkbootstrap.core import App
from ttkbootstrap.widgets import LabelFrame
from ttkbootstrap.widgets.icon_button import IconButton

from ttkbootstrap.layouts.pack_frame import PackFrame

with App(theme="dark") as app:

    app.geometry("800x600")

    with PackFrame(padding=8, justify="stretch") as layout:
        layout.add(IconButton(icon='house-fill'))
        layout.add(IconButton(icon='search'))
        layout.add(IconButton(icon='trash-fill', color='danger'))
        layout.mount()

    with LabelFrame(padding=8) as label_frame:
        with PackFrame(padding=8, justify="stretch") as layout:
            layout.add(IconButton(icon='amd'))
            layout.add(IconButton(icon='archive-fill'))
            layout.add(IconButton(icon='android', color='success'))
            layout.mount()
        label_frame.add(layout)
        label_frame.mount()

    app.run()


# app = App(theme="dark")
# app.geometry("800x600")
#
# layout = PackLayout(app, fill='x')
# layout.add(IconButton(layout, icon='house-fill'))
# layout.add(IconButton(layout, icon='search'), expand=True)
# layout.add(IconButton(layout, icon='trash-fill', color='danger'))
# layout.pack(fill='x', padx=8, pady=(8, 0))
#
# layout = PackLayout(app, fill='x')
# layout.add(IconButton(layout, icon='amd'))
# layout.add(IconButton(layout, icon='archive-fill'), expand=True)
# layout.add(IconButton(layout, icon='android', color='success'))
# layout.pack(fill='x', padx=8, pady=(4, 0))
#
# app.run()