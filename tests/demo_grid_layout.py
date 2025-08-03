from ttkbootstrap.core import App
from ttkbootstrap.widgets import Canvas, DateEntry, IconButton, GridLayout, TextEntry
from ttkbootstrap.widgets.layout.pack_layout import PackLayout

app = App(theme='dark')
app.geometry('800x600')

pack = PackLayout(app, padding=8, fill='x').pack(fill='x')
pack.add(IconButton(pack, icon='house'))
pack.add(DateEntry(pack), expand=True)
pack.add(IconButton(pack, icon='search'))

app.run()