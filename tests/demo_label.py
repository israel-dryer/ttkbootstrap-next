from ttkbootstrap import App, Pack, Label

icon = {"name": "house-fill", "size": 24}

with App("Label Demo") as app:
    with Pack(padding=16).attach():
        lbl = Label("Hello world", icon=icon, compound="left", anchor="center", font="xl").attach()

    print(lbl.configure('image'))
    print(lbl.configure('text'))
    print(lbl.configure('style'))

app.run()
