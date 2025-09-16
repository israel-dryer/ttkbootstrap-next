from ttkbootstrap import App, Pack, Button

with App("Demo Button") as app:
    with Pack(padding=16).layout(fill="x"):
        b = Button(icon="house-fill")
        Button("House", icon="house", on_invoke=lambda: b.icon("airplane"))
        Button("House", icon="house-fill").on_invoke(lambda: b.icon("house-fill"))
        Button("House", icon="house-fill", color="warning")
        Button(icon="house", variant="outline", on_invoke=lambda e: print(e))
        Button(icon="house", variant="ghost", color="dark", on_invoke=lambda: app.theme.use('light'))
        Button("House", icon="house", variant="outline", on_invoke=lambda: app.theme.use('dark'))
app.run()
