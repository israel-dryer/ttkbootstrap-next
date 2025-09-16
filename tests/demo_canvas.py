from ttkbootstrap import App, Pack, Button, Canvas, Scrollbar

with App("Demo Canvas - Scrollbar") as app:
    with Pack(padding=16).layout(fill="both", expand=True):
        scrollbar = Scrollbar(orient="vertical", position="fixed").layout(x="100%", height="100%")
        vbar_width = scrollbar.width()
        scrollbar.layout(merge=True, xoffset=-vbar_width + 3)
        with Canvas(on_yview_change=scrollbar.set).layout(fill="both", expand=True) as canvas:
            canvas.add_widget(100, 100, Button("Hello"))
            scrollbar.on_scroll(canvas.yview)
            scrollbar.widget.lift()
app.run()
