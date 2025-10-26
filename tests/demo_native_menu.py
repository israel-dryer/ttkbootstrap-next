from ttkbootstrap import App, Label, Pack
from ttkbootstrap.icons.bootstrap import BootstrapIcon
from ttkbootstrap.widgets.menu import NativeMenu
from tkinter import ttk

with App(geometry="800x800", theme="dark") as app:
    with Pack().attach(fill='both', expand=True):
        Label("Native Menu Demo", anchor="center", font="display-xl").attach(fill='both', expand=True)

    system_menu = NativeMenu(app)
    file_menu = NativeMenu(system_menu)
    system_menu.add_cascade(label="File", menu=file_menu.widget)
    file_menu.add_command(
        label="Open", image=BootstrapIcon("card-image", size=10, color="white").image, compound="left")
    file_menu.add_command(label="Close", image=BootstrapIcon("archive", size=10, color="white").image, compound="left")
    file_menu.add_separator()
    file_menu.add_command(
        label="Exit", image=BootstrapIcon("door-closed-fill", size=10, color="white"), compound="left")
    app.configure(menu=system_menu.widget)

    ttk.Button(app.widget, image=BootstrapIcon(name="house-fill").image).pack()

app.run()
