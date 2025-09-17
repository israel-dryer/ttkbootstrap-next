from ttkbootstrap import App, Button, Fieldset

with App("Fieldset Demo") as app:
    with Fieldset("My Stuff", "A thing about my stuff", collapsible=True).layout(fill='both', expand=True) as fs:
        Button("Push")

app.run()
