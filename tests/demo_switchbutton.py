from ttkbootstrap.core import App
from ttkbootstrap.widgets import Frame
from ttkbootstrap.widgets.buttons.switch_button import SwitchButton

app = App()

frame = Frame(app, padding=16).pack()

SwitchButton(frame, "Air Conditioning", width=100).pack()
SwitchButton(frame, "Water Softener", value=1, width=100).pack()

app.run()