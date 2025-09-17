from ttkbootstrap import App, Button, Checkbutton, Expander, Label, NumericEntry, Pack, TextEntry

with App("Fieldset Demo", geometry="600x300", theme="dark") as app:
    with Pack(padding=16, gap=16).layout(fill='both', expand=True):
        with Expander(title="My Stuff", collapsible=True).layout(fill='both') as ex:
            with ex.content:
                Button("Push")

        with Expander(title="Default", collapsible=True).layout(fill='both') as ex:
            with ex.header:
                Checkbutton()
                Label("Custom Header Label")
            with ex.content:
                with Pack(padding=1).layout(fill='both', expand=True):
                    with Pack(fill_items='x', padding=16).layout(fill='both', expand=True):
                        TextEntry(label="First Name")
                        TextEntry(label="Last Name")
                        NumericEntry(label="Age")
                        TextEntry(label="Occupation")

app.run()
