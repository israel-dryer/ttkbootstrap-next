from ttkbootstrap.core import App
from ttkbootstrap.widgets import CheckButton, RadioButton

app = App()

RadioButton(app, "One", 1, 'Numbers', selected=True).pack().disable()
RadioButton(app, "Two", 2, "Numbers").pack()
RadioButton(app, "Three", 3, "Numbers").pack().disable()
CheckButton(app, "Something").pack()

app.run()