from ttkbootstrap.core import App
from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.layout.pack_frame import PackFrame

with App("Demo App") as app:

    with PackFrame(padding=16, direction="row", justify="stretch", align="stretch", expand=True) as frame:
        (
            frame
                << Button(text="Hello1", color="warning", align="top")
                << Button(text="Hello2", color="light", expand=True, align="stretch", justify="stretch")
                << Button(text="Hello3", color="danger", align="bottom")
        )

app.run()