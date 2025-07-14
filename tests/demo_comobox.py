import tkinter
from tkinter import ttk, Tk, Listbox

ttk.Combobox()


root = Tk()
lb = Listbox(root)
for x in range(20):
    lb.insert('end', x)
lb.pack()

root.mainloop()