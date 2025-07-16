from ttkbootstrap.core import App
from ttkbootstrap.widgets import CheckButton

app = App(title="Demo Checkbutton", theme="dark")

cb1 = CheckButton(app, text="Unchecked", color="success", value=0).pack()
CheckButton(app, text="Unchecked", color="success", value=0).pack()
CheckButton(app, text="Unchecked", value=0).pack()
cb2 = CheckButton(app, text="Indeterminate", value=-1, on_toggle=lambda: print('Clicked')).pack()
cb3 = CheckButton(app, text="Checked", value=1, on_change=lambda x: print(x)).pack()
print('one', cb1.state())
print('two', cb2.state())
print('three', cb3.state())

app.run()

# import tkinter as tk
# from tkinter import ttk
#
# root = tk.Tk()
# style = ttk.Style()
# style.theme_use('clam')
#
# print(style.layout('TCheckbutton'))
# print(style.map('TCheckbutton'))
#
# ttk.Checkbutton(root).pack()
#
# root.mainloop()