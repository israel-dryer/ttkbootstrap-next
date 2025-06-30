from ttkbootstrap.core import App
from ttkbootstrap.widgets.button import Button

app = App("Button Demo")

btn = Button(app, "Push me").pack().on_click(lambda: print("Hello world"))

app.run()