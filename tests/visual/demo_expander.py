from ttkbootstrap_next import App, Button, Checkbutton, Expander, Label, NumericEntry, Pack, TextEntry

with App("Fieldset Demo", geometry="600x300") as app:
    with Pack(padding=16, gap=16).attach(fill='both', expand=True):
        with Expander("This is the expander title", border=True, button_position='before').attach(fill='both') as ex:
            with ex.content:
                Button("Push").attach()

        with Expander("This is the expander title", border=True).attach(fill='both') as ex:
            with ex.content:
                Button("Push").attach()

        with Expander("This is the expander title", border=True, collapsible=False).attach(fill='both') as ex:
            with ex.content:
                Button("Push")

        with Expander("Default", border=True, button_position='before').attach(fill='both') as ex:
            with ex.header:
                Checkbutton().attach()
                Label("Custom Header Label").attach()
            with ex.content:
                with Pack(fill_items='x').attach(fill='both'):
                    te = TextEntry(label="First Name").attach()
                    TextEntry(label="Last Name").attach()
                    NumericEntry(label="Age").attach()
                    TextEntry(label="Occupation").attach()

app.run()
