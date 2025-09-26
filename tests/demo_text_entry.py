from ttkbootstrap import App, Grid, Button, Label, TextEntry, Event

with App("Text Entry Demo", geometry="600x400") as app:
    with Grid(padding=16, columns=2, gap=8, sticky_items="ew").layout(fill="x"):
        TextEntry(label="First Name", required=True).layout(columnspan=2).on_validated(lambda e: print(e))
        TextEntry("16228 Kelby Cove", label="Address").layout(columnspan=2).on_input(lambda x: print(x)).on_enter(
            lambda x: print(x)).on_changed(lambda x: print(x))
        TextEntry("July 15, 2025", label="Birthday", display_format="shortDate")
        occupation = TextEntry(label="Email", required=True).layout(columnspan=2)
        occupation.insert_addon(Label, text="@", position="left")
        Button("Submit", icon="moon").on_invoke().listen(lambda _: app.theme.use("dark"))
        Button("On Handler").on(Event.CLICK).filter(lambda e: e.x > 100).listen(lambda x: print(x))
        Button("Cancel", variant="outline", icon="sun").on_invoke().tap(lambda _: app.theme.use('light')).then_stop()
app.run()
