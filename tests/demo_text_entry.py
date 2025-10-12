from ttkbootstrap import App, Button, Event, Grid, Label, TextEntry

with App("Text Entry Demo", geometry="600x400") as app:
    with Grid(padding=16, columns=2, gap=8, sticky_items="ew").attach(fill="x"):
        TextEntry(label="First Name", required=True).attach(columnspan=2).on_validated().listen(lambda e: print(e))
        te = TextEntry("16228 Kelby Cove", label="Address").attach(columnspan=2)
        te.on_input().listen(lambda x: print(x))
        te.on_enter().listen(lambda x: print(x))
        te.on_changed().listen(lambda x: print(x))
        TextEntry("July 15, 2025", label="Birthday", value_format="shortDate").attach()
        occupation = TextEntry(label="Email", required=True).attach(columnspan=2)
        occupation.insert_addon(Label, text="@", position="left")
        Button("Submit", icon="moon").attach().on_invoke().listen(lambda _: app.theme.use("dark"))
        Button("On Handler").attach().on(Event.CLICK).filter(lambda e: e.x > 100).listen(lambda x: print(x))
        Button("Cancel", variant="outline", icon="sun").attach().on_invoke().tap(
            lambda _: app.theme.use('light')).then_stop()
app.run()
