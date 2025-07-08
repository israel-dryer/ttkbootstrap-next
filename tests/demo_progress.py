from ttkbootstrap.core import App
from ttkbootstrap.widgets import Progress

app = App(title="Demo Progress")

Progress(app, value=25).pack(fill='x', padx=16, pady=16)
pb1 = Progress(app, mode="indeterminate").pack(fill='x', padx=16, pady=16)
pb1.start()

app.run()