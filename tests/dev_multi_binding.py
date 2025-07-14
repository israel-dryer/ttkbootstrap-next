from ttkbootstrap.core import App
from ttkbootstrap.widgets import Button

app = App()

b1 = Button(app, text='Button1').pack(pady=16)
b2 = Button(app, text='Button2').pack(pady=16)
#
# b1.bind('mouse_down', lambda e: print('clicking button 1 binding 1'))
# b1.bind('mouse_down', lambda e: print('clicking button 1 binding 2'))

app.run()