from ttkbootstrap import App
from ttkbootstrap.layouts.flexgrid import FlexGrid
from ttkbootstrap.widgets import Button, Canvas, Scrollbar

with App(theme="dark") as app:

    with FlexGrid():
        canvas = Canvas(sticky="nsew", expand=True)
        vsb = Scrollbar(orient="vertical", command=canvas.yview, position="absolute")
        vsb.place(x="100%", offset_x=-16, height="100%")

        # set canvas scroll commands
        canvas.configure(yscrollcommand=vsb.set)
        canvas.add_widget(100, 100, Button(canvas, text="hello"))

app.run()

