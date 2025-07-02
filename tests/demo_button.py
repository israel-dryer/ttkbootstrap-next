from ttkbootstrap.core import App
from ttkbootstrap.widgets.button import Button

app = App("Button Demo", surface="accent")

b1 = Button(app, "Primary", color="primary", icon="house").pack(padx=16, pady=16).disable()
b2 = Button(app, "Primary", color="primary", icon="house").pack(padx=16, pady=16)
Button(app, "Primary", color="primary").pack(padx=16, pady=16)
Button(app, "Secondary", color="secondary", size="lg", icon="house").pack(padx=16, pady=16)
Button(app, "Success", color="success", size="sm", icon="chevron-right", compound="right").pack(padx=16, pady=16)
Button(app, "Warning", color="warning").pack(padx=16, pady=16)
Button(app, "Danger", color="danger").pack(padx=16, pady=16)
ac = Button(app, "Accent Bg", color="info").pack(padx=16, pady=16)
lt = Button(app, "Light", color="light").pack(padx=16, pady=16)
tb = Button(app, "Dark", color="dark").pack(padx=16, pady=16)

ac.on_click(lambda: app.surface('muted'))
tb.on_click(lambda: app.theme.use('dark'))
lt.on_click(lambda: app.theme.use('light'))

app.run()
