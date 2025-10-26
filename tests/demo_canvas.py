from ttkbootstrap_next import App, Button, Canvas, Pack, Scrollbar

with App("Demo Canvas - Scrollbar") as app:
    with Pack(padding=16).attach(fill="both", expand=True):
        scrollbar = Scrollbar(orient="vertical").attach("place", x="100%", height="100%")
        vbar_width = scrollbar.width()
        scrollbar.attach("place", xoffset=-vbar_width + 3)
        with Canvas(yscroll_command=scrollbar.set).attach(fill="both", expand=True) as canvas:
            canvas.add_widget(100, 100, Button("Hello"))
            scrollbar.configure(command=canvas.yview)
            scrollbar.widget.lift()
app.run()
