from ttkbootstrap.core.app import App
from tkinter import ttk

app = App("Demo App")

ttk.Label(app, text="Hello World", font="display_lg").pack()

app.run()