import tkinter as tk
from tkinter import ttk

from ttkbootstrap.core import App
from ttkbootstrap.style.typography import Typography

root = App("Typography Demo")

for token in Typography.all()._fields:
    label = ttk.Label(root, text=token.replace("_", " ").title(), font=token)
    label.pack(anchor="w", pady=2)

ttk.Label(root, text="Demo", font="display_lg").pack()

root.run()
