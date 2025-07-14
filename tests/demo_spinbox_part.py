from ttkbootstrap.core import App
from ttkbootstrap.widgets.parts.number_spinbox_part import NumberSpinboxPart

app = App()

NumberSpinboxPart(app, value=0.0, increment=0.1).pack(padx=16, pady=16, fill='x').on_change(lambda x: print(x)).on_enter(lambda x:print(x))
NumberSpinboxPart(app, value=0.0, increment=0.1).pack(padx=16, pady=16, fill='x').on_change(lambda x: print(x)).on_enter(lambda x:print(x))

app.run()