from ttkbootstrap.core import App
from ttkbootstrap.widgets import Label, Frame
from ttkbootstrap.style.typography import Typography

root = App("Typography Demo")

frame = Frame(root, padding=32).pack()

for token in Typography.all()._fields:
    label = Label(frame, text=token.replace("_", " ").title(), font=token.replace('_', '-'))
    label.pack(anchor="w", pady=2)

root.run()
