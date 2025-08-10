from ttkbootstrap import App
from ttkbootstrap.layouts.gridbox import GridBox
from ttkbootstrap.layouts.pack_frame import PackFrame
from ttkbootstrap.widgets import Button, Canvas, Label, Scrollbar

with App(theme="dark") as app:

    with PackFrame(expand=True, sticky="nsew", padding=16):
        with GridBox(columns=[1, 0], rows=[1, 0], sticky="nsew", expand=True):
            canvas = Canvas(sticky="nsew", expand=True)
            vsb = Scrollbar(orient="vertical", command=canvas.y_view, sticky="ns")
            hsb = Scrollbar(orient="horizontal", command=canvas.x_view, sticky="sew", colspan=2)

        # set canvas scroll commands
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        canvas.add_widget(100, 100, Button(canvas, text="hello"))

app.run()
    #scrollable_frame = PackFrame(canvas, width=2000, height=2000)

#
# # Internal frame with hardcoded width for horizontal overflow
# scrollable_frame = Frame(canvas, width=2000, height=800)  # hard-coded size
# window_id = canvas.add_widget(0, 0, scrollable_frame, anchor="nw")
#
# # Update scrollregion to enable scrolling
# def on_frame_configure(event):
#     canvas.configure(scrollregion=canvas.get_bounding_box("all"))
#
# scrollable_frame.bind("<Configure>", on_frame_configure)
#
# # Example content to overflow horizontally
# for i in range(50):
#     Label(
#         scrollable_frame,
#         text=f"Item {i} - " + "✦" * 10,
#         anchor="w"
#     ).place(x=i * 150, y=i * 30)  # absolute placement for demo
#
# root.run()
