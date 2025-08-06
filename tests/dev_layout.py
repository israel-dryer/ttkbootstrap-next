from ttkbootstrap.core import App
from ttkbootstrap.widgets import Button
from ttkbootstrap.widgets.layout.pack_frame import PackFrame

# with App("Demo App", theme="dark") as app:
#
#     with PackFrame(padding=16, direction="column", justify="stretch", align="stretch", expand=True) as frame:
#         (
#             frame
#                 << Button(text="Hello1", color="warning", align="top")
#                 << Button(text="Hello2", color="light", expand=True, align="stretch", justify="stretch")
#                 << Button(text="Hello3", color="danger", align="bottom")
#         )
#
# app.run()


with App("Demo App", theme="dark") as app:

    with PackFrame(direction="column", justify="stretch", align="stretch", expand=True):
        Button(text="Hello1", color="warning", align="top")
        Button(text="Hello2", color="success", expand=True, align="stretch", justify="stretch")
        Button(text="Hello3", color="danger", align="bottom")

        with PackFrame(padding=16, direction="row", justify="stretch", align="stretch", expand=True):
            Button(text="Hello1", color="warning", align="top")
            Button(text="Hello2", color="primary", expand=True, align="stretch", justify="stretch")
            Button(text="Hello3", color="danger", align="bottom")


app.run()
