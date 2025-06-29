import tkinter as tk
from tkinter import ttk
from ttkbootstrap.style.typography import Typography

root = tk.Tk()
root.title("Typography Demo")

Typography.use_fonts()

for token in Typography.all()._fields:
    font = Typography.get_font(token)
    label = ttk.Label(root, text=token.replace("_", " ").title(), font=font)
    label.pack(anchor="w", pady=2)

root.mainloop()
