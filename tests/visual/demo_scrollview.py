
import tkinter as tk

root = tk.Tk()

canvas = tk.Canvas(root)
canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(root, command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set, )
print(canvas.yview('moveto', 0.5))

print(canvas.yview())

root.mainloop()