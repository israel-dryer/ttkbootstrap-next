from ttkbootstrap.app import App
from ttkbootstrap.layouts import Pack
from ttkbootstrap.widgets import Progressbar

with App("Demo Progressbar") as app:
    with Pack(padding=16, gap=8, fill_items="x").layout(fill="x"):
        Progressbar(75, "primary")
        Progressbar(75, "secondary")
        Progressbar(75, "success").start(8)
        Progressbar(75, "warning")
        Progressbar(75, "danger")
        Progressbar(75, "light")
        Progressbar(75, "dark")

        Progressbar(75, "primary", variant="striped")
        Progressbar(75, "secondary", variant="striped")
        Progressbar(75, "success", variant="striped")
        Progressbar(75, "warning", variant="striped")
        Progressbar(75, "danger", variant="striped").start(5)
        Progressbar(75, "light", variant="striped").start()
        Progressbar(75, "dark", variant="striped", mode="indeterminate").start()

app.run()