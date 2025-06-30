

from tkinter import Tk, ttk

root = Tk()
style = ttk.Style()

style.configure('TFrame', background="blue")
bg = style.configure('TFrame', 'background')

frame = ttk.Frame(root)
btn = ttk.Button(frame, text="Push", command=lambda: style.configure('TFrame', background="red"))

frame.pack(fill='both', expand=1)
btn.pack()

##print(frame.configure('style'))
##print(btn.configure('background'))
##print(root.configure('background'))



print('background color:', bg)
root.mainloop()