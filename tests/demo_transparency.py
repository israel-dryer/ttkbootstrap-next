
import tkinter as tk

root = tk.Tk()
root.geometry('300x300')
root.title('demo transparency')
root.configure(bg='magenta')
tk.Label(root, text="Hello World", background="red", padx=16, pady=16).pack(fill='both', expand=True, anchor="center")

def show_toplevel():
    top = tk.Toplevel()
    top.geometry('300x300')
    top.configure(background="magenta")
    top.attributes('-transparentcolor', 'magenta')


tk.Button(root, text='Show Toplevel', command=show_toplevel).pack(padx=16, pady=16)

root.mainloop()