from ttkbootstrap import App, Pack, Button

with App("Demo Button") as app:
    with Pack(padding=16).layout(fill="x"):
        b = Button(icon="house-fill")
        Button("House", icon="house", command=lambda: b.configure(icon="airplane"))
        Button("House", icon="house-fill").on_invoke().listen(lambda *_: b.configure(icon="house-fill"))
        Button("House", icon="house-fill", color="warning").on_invoke().listen(lambda e: print(e))
        Button(icon="house", variant="outline", command=lambda e: print(e))
        Button(icon="house", variant="ghost", color="dark", command=lambda: app.theme.use('light'))
        Button("House", icon="house", variant="outline", command=lambda: app.theme.use('dark'))
app.run()
