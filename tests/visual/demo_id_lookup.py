from ttkbootstrap_next import App, Pack, Badge
from ttkbootstrap_next.core.widget_registry import lookup

with App() as app:
    with Pack(padding=16, gap=8):
        Badge("21+", id="regular")
        Badge("2", variant="circle", id="circle")
        Badge("355 lbs", variant="pill", id="pill")

widget = lookup("regular")
widget.text("updated")
print(widget, widget.tk_name)

app.run()
