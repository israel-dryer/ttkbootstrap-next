from ttkbootstrap import App, Button, Pack

icon = {
    "name": "house",
    "state": {"hover": "house-fill", "pressed": "apple"}
}

with App("Demo Button") as app:
    with Pack(padding=16).attach(fill="x"):
       b = Button("House", icon=icon).attach()
       Button("House", icon="house-fill").attach().on_invoke().listen(lambda *_: b.configure(icon="house-fill"))
       Button("House", icon="house-fill", color="warning").attach().on_invoke().listen(lambda e: print(e))
       Button(icon="house", variant="outline", command=lambda e: print(e)).attach()
       Button(icon="house", variant="ghost", color="dark", command=lambda: app.theme.use('light')).attach()
       Button("House", icon="house", variant="outline", command=lambda: app.theme.use('dark')).attach()
app.run()
