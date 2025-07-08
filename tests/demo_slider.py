from ttkbootstrap.core import App
from ttkbootstrap.widgets import Slider

app = App(title="Scale Demo")

scale = Slider(app, value=25, on_change=lambda x: print(x)).pack(padx=16, pady=16, fill='x')


app.run()