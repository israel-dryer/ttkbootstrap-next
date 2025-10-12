from ttkbootstrap import App, Pack, Label

with App("Label Demo") as app:
    with Pack(padding=16).attach():
        Label("Hello world", icon="house-fill", compound="left", anchor="center", font="body-xl").attach()

app.run()
