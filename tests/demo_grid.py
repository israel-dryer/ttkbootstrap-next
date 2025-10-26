# ttk bootstrap

# from ttkbootstrap_next import App, Button, Grid
#
# with App("Demo Grid Layout") as app:
#     with Grid(rows=[0, 1, 0], columns=[0, 1, 0], padding=8, gap=8).attach(fill='both', expand=True):
#         for x in range(4):
#             Button(text="Button", icon="house-fill").attach(sticky="nsew")
#             Button(icon="house-fill", variant="outline").attach(sticky="")
# app.run()


# tkinter
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Demo Grid Layout")

# Grid container with internal padding (like padding=8)
container = ttk.Frame(root, padding=8)
container.pack(fill="both", expand=True)

# rows=[0,1,0], columns=[0,1,0]
row_weights    = [0, 1, 0]
column_weights = [0, 1, 0]
for r, w in enumerate(row_weights):
    container.rowconfigure(r, weight=w)
for c, w in enumerate(column_weights):
    container.columnconfigure(c, weight=w)

GAP = 8
NUM_COLS = len(column_weights)

# We add 8 buttons total (two per loop like your example)
# 1st button: sticky="nsew"
# 2nd button: sticky="" (no expansion)
buttons = []
for i in range(8):
    r, c = divmod(i, NUM_COLS)
    # gap: only on non-first col/row
    padx = (GAP, 0) if c > 0 else 0
    pady = (GAP, 0) if r > 0 else 0

    # In plain ttk there’s no `icon=` option; using text only here
    text = "Button" if i % 2 == 0 else "Outline"
    btn = ttk.Button(container, text=text)

    sticky = "nsew" if i % 2 == 0 else ""
    btn.grid(row=r, column=c, padx=padx, pady=pady, sticky=sticky)
    buttons.append(btn)

root.mainloop()
