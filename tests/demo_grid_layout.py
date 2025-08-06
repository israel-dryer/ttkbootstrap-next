from ttkbootstrap.core import App
from ttkbootstrap.widgets import GridFrame, LabelFrame
from ttkbootstrap.widgets.icon_button import IconButton
from ttkbootstrap.layouts.pack_frame import PackFrame

with App(theme="dark") as app:

    app.geometry("800x600")

    with GridFrame(padding=(8, 8, 8, 0), gap=(4, 0)) as layout:
        layout.add(IconButton(icon='house-fill'), colspan=3)
        layout.add(IconButton(icon='search'), colspan=6)
        layout.add(IconButton(icon='trash-fill', color='danger'), colspan=3)
        layout.pack(fill='x', padx=16, pady=16)

    with LabelFrame(text="Button Items") as l_frame:
        with PackFrame(padding=8, gap=(4, 0), fill='x') as layout:
            layout.add(IconButton(icon='amd'))
            layout.add(IconButton(icon='archive-fill'), expand=True)
            layout.add(IconButton(icon='android', color='success'))
            l_frame.add(layout)

        l_frame.pack(fill='x', padx=16, pady=16)

    app.run()
