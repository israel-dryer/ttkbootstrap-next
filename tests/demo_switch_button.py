from ttkbootstrap import App, Pack, Switch

with App("Demo Switch Button") as app:
    with Pack(padding=16, fill_items="x", gap=16):
        Switch("Air Conditioning", 0)
        Switch("Water Softener", 1, color="danger")
        Switch("Something Else")
app.run()
