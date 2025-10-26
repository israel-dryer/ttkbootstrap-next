from ttkbootstrap_next import App, TextEntry, DateEntry, Pack, PasswordEntry, PathEntry, NumericEntry, Label

with App("Entry Demo") as app:
    with Pack(padding=16, gap=8, direction="column", fill_items='x').attach():
        TextEntry("Israel", label="First Name", required=True).attach()
        NumericEntry(124000, label="Range", value_format="currency").attach()
        DateEntry("March 14, 1981", value_format="shortDate").attach()
        PasswordEntry("mypassword", label="Password", show_visible_toggle=True).attach()
        PathEntry().attach()

        # custom email entry

        te = TextEntry("israel.dryer@gmail.com", label="Email")
        te.insert_addon(Label, text="@", position="left")
        te.add_validation_rule("email")
        te.attach()


app.run()
