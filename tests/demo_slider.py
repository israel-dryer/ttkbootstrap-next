from ttkbootstrap.core import App
from ttkbootstrap.widgets import Scale

app = App(title="Scale Demo")

Scale(app, color="success", value=40, orient="vertical").pack(padx=16, pady=16, fill="y", expand=True)

app.run()


