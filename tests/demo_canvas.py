from ttkbootstrap.core import App
from ttkbootstrap.widgets import Canvas, Frame, Label, Scrollbar

root = App(theme="dark")

# Outer container
container = Frame(root)
container.pack(fill="both", expand=True)

# Canvas inside the container
canvas = Canvas(container)
canvas.pack(side="left", fill="both", expand=True)

# Vertical scrollbar
vsb = Scrollbar(container, orient="vertical", command=canvas.y_view)
vsb.pack(side="right", fill="y")

# Horizontal scrollbar
hsb = Scrollbar(root, orient="horizontal", command=canvas.x_view)
hsb.pack(side="bottom", fill="x")

canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

# Internal frame with hardcoded width for horizontal overflow
scrollable_frame = Frame(canvas, width=2000, height=800)  # hard-coded size
window_id = canvas.add_widget(0, 0, scrollable_frame, anchor="nw")

# Update scrollregion to enable scrolling
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.get_bounding_box("all"))

scrollable_frame.bind("<Configure>", on_frame_configure)

# Example content to overflow horizontally
for i in range(50):
    Label(
        scrollable_frame,
        text=f"Item {i} - " + "✦" * 10,
        anchor="w"
    ).place(x=i * 150, y=i * 30)  # absolute placement for demo

root.run()
