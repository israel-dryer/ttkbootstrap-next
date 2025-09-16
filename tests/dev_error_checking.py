from tkinter import ttk
import tkinter


root = tkinter.Tk()

nb = ttk.Notebook(root)
nb.pack()

result = nb.select()

value = nb.tab('123', 'text')
print('result', result)

root.mainloop()