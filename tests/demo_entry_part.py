from ttkbootstrap.core import App
from ttkbootstrap.widgets.parts import EntryPart

app = App()

EntryPart(app).pack(padx=16, pady=16).on_changed(lambda x: print('changed', x)).add_validation_rule('required').on_validated(lambda x: print(x))
EntryPart(app).pack(padx=16, pady=16)
app.run()
