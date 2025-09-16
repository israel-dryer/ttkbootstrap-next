from ttkbootstrap import App, Pack, Label

with App("Label Demo") as app:
    with Pack(padding=16):
        Label("Hello world", icon="house-fill", icon_position="end", anchor="center", font="body-xl")

app.run()
