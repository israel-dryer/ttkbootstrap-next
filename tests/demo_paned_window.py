from ttkbootstrap.core import App
from ttkbootstrap.widgets import Frame
from ttkbootstrap.widgets.layout.paned_window import PanedWindow

app = App()

pw = PanedWindow(app, sash_color="blue-200")
pw.pack(fill='both', expand=1)

pw.add(Frame(pw, surface="layer-1", width=500, height=500))
pw.add(Frame(pw, surface="layer-2", width=500, height=500))

app.run()
