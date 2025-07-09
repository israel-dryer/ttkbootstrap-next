from ttkbootstrap.core import App
from ttkbootstrap.widgets import Canvas, Frame, Label, Scrollbar

root = App(theme="dark")

frame = Frame(root)
frame.pack(fill="both", expand=True)

canvas = Canvas(frame)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = Scrollbar(frame, orient="vertical", command=canvas.y_view)
scrollbar.pack(side="right", fill="y")

canvas.configure(yscrollcommand=scrollbar.set)

# Create a scrollable frame inside the canvas
scrollable_frame = Frame(canvas)
canvas.add_widget(0, 0, scrollable_frame)

# Update scrollregion when contents change
def on_configure(event):
    canvas.configure(scrollregion=canvas.get_bounding_box("all"))

scrollable_frame.bind("<Configure>", on_configure)

# Example content
for i in range(50):
   Label(scrollable_frame, text=f"Item {i}").pack()

root.run()
