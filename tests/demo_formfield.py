from ttkbootstrap.core import App
from ttkbootstrap.widgets import Frame, NumberEntry, Button, FileEntry, Label
from ttkbootstrap.widgets.date_entry import DateEntry
from ttkbootstrap.widgets.password_box import PasswordEntry
from ttkbootstrap.widgets.text_entry import TextEntry

app = App()

frame = Frame(app, padding=16).pack(fill='both')
ne = NumberEntry(frame, value="1", label="Age", message="When you were born").pack(pady=16, fill='x').insert_addon(Label, position="left", text="$")
ne.insert_addon(Label, text='.00', pack_options={"after": ne.increment_widget})

NumberEntry(frame,
            value="1",
            label="Age",
            message="When you were born",
            show_spin_buttons=False).pack(pady=16, fill='x')

DateEntry(frame, value="March 14, 1981", label="Date of Birth").pack(fill='x')

te = TextEntry(frame, value="israel.dryer@gmail.com", label="Email").pack(fill='x', pady=16)
te.insert_addon(Label, text="@", position="left")
TextEntry(frame, value="Israel Dryer", label="First Name", message="What are you called?").pack(fill='x', pady=16).readonly(True).insert_addon(Label, text="@", position="left")

PasswordEntry(frame, value="Top Secret", label="Password", message="This is a password").pack(fill='x', pady=16).add_validation_rule("required")
PasswordEntry(frame, value="Top Secret", label="Password", show_visible_toggle=True).pack(fill='x', pady=16)

FileEntry(frame).pack(fill='x')

app.run()
