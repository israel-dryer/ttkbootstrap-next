from ttkbootstrap import App
from ttkbootstrap.style.theme import ColorTheme
from ttkbootstrap.widgets.button import Button

app = App(theme="dark")

theme = ColorTheme.instance()


Button(app, 'primary', color='primary', icon="house").pack(padx=16, pady=16)
# Button(app, 'secondary', color="secondary", icon="house").pack(padx=16, pady=16)
# Button(app, 'info', color="info").pack(padx=16, pady=16).disable()
# Button(app, 'success', color="success", icon="house").pack(padx=16, pady=16)
# Button(app, 'warning', color="warning").pack(padx=16, pady=16).disable()
# Button(app, 'danger', color="danger").pack(padx=16, pady=16).disable()
# Button(app, 'danger', color="danger").pack(padx=16, pady=16)
# Button(app, 'light', color="light").pack(padx=16, pady=16)
# Button(app, 'dark', color="dark").pack(padx=16, pady=16)

# Button(app, 'primary', color='primary', icon="house", variant="outline").pack(padx=16, pady=16)
# Button(app, 'secondary', color="secondary", icon="house", variant="outline").pack(padx=16, pady=16)
# Button(app, 'info', color="info", variant="outline").pack(padx=16, pady=16)
# Button(app, 'success', color="success", variant="outline").pack(padx=16, pady=16)
# Button(app, 'warning', color="warning", icon="house", variant="outline").pack(padx=16, pady=16).disable()
# Button(app, 'danger', color="danger", variant="outline").pack(padx=16, pady=16)
# Button(app, 'light', color="light", variant="outline").pack(padx=16, pady=16)
# Button(app, 'dark', color="dark", variant="outline").pack(padx=16, pady=16)

# Button(app, 'primary', icon="house", color='primary', variant="ghost").pack(padx=16, pady=16)
# Button(app, 'secondary', icon="house", color="secondary", variant="ghost").pack(padx=16, pady=16)
# Button(app, 'info', color="info", variant="ghost").pack(padx=16, pady=16)
# Button(app, 'success', color="success", variant="ghost").pack(padx=16, pady=16)
# Button(app, 'warning', icon="house", color="warning", variant="ghost").pack(padx=16, pady=16).disable()
# Button(app, 'danger', color="danger", variant="ghost").pack(padx=16, pady=16)
# Button(app, 'light', color="light", variant="ghost").pack(padx=16, pady=16)
# Button(app, 'dark', color="dark", variant="ghost").pack(padx=16, pady=16)

app.run()
