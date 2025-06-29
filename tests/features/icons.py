from tkinter import Tk
from tkinter import ttk

from ttkbootstrap.icons import BootstrapIcon, LucideIcon

root = Tk()

bs_icon = BootstrapIcon("plus")
lucide_icon = LucideIcon("plus")

ttk.Label(image=lucide_icon, compound="image").pack()
ttk.Label(image=bs_icon, compound="image").pack()


root.mainloop()