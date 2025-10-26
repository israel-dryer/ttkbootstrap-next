from ttkbootstrap_next import App, Pack, Switch

with App("Demo Switch Button") as app:
    with Pack(padding=16, fill_items="x", gap=16).attach(fill="both", expand=True):
        Switch("Air Conditioning", 0).attach()
        Switch("Water Softener", 1, color="danger").attach()
        Switch("Something Else").attach()
app.run()
