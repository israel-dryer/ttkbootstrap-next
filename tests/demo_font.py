import tkinter as tk
from tkinter import font

root = tk.Tk()

# Create a named font
myfont = font.Font(name="MyCustomFont", family="Segoe UI", size=24, weight="bold")

# Use the named font in a widget
label = tk.Label(root, text="Hello, World!", font="MyCustomFont")
label.pack()

root.mainloop()
