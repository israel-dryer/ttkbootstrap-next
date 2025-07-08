import tkinter as tk
from tkinter import ttk

root = tk.Tk()

style = ttk.Style()
style.theme_use('clam')

options = style.configure('TSizegrip')
print(options)