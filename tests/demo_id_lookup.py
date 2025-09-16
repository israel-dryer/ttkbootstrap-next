from ttkbootstrap.app import App
from ttkbootstrap.core.widget_registry import lookup
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Badge

with App() as app:
    with Pack(padding=16, gap=8):
        Badge("21+", id="regular")
        Badge("2", variant="circle", id="circle")
        Badge("355 lbs", variant="pill", id="pill")


widget = lookup("regular")
widget.text("updated")
print(widget, widget.tk_name)

app.run()
