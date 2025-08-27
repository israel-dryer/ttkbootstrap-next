from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Badge

with App() as app:
    with Pack(padding=16, gap=8):
        Badge("21+")
        Badge("2", variant="circle")
        Badge("355 lbs", variant="pill")
app.run()