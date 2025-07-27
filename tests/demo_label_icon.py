from ttkbootstrap.core import App
from ttkbootstrap.widgets import Label

app = App(theme="dark")

Label(app, text="Hello", icon="house-fill", compound="left").pack()
Label(app, text="Hello", icon=dict(name="house-fill", size=25, color="yellow"), compound="left").pack()

app.run()