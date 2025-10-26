from ttkbootstrap_next import App, DateEntry, Pack

with App("Demo Date Entry") as app:
    with Pack(padding=16, gap=8).attach():
        de = DateEntry("March 14, 1981", "Birthdate", "Required", value_format="longDate").attach()
        de.add_validation_rule("required", message="This is required")
        de.on_validated().listen(lambda x: print(x))
        DateEntry().attach()
app.run()
