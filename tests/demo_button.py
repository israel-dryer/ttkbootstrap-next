from ttkbootstrap import App
from ttkbootstrap.style.theme import ColorTheme
from ttkbootstrap.widgets import CheckButton, IconButton, RadioButton, Button
from ttkbootstrap.layouts.pack_frame import PackFrame
from ttkbootstrap.layouts.gridbox import GridBox


class ButtonFrameSection(PackFrame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # add children
        with PackFrame(parent=self):
            self._theme_button = IconButton(icon='moon-fill', variant="ghost", on_click=self.toggle_theme)
            IconButton(icon='house-fill', variant="ghost")
            IconButton(icon='bag-check-fill', variant="ghost")
            CheckButton(text='Is Deployed')

    def toggle_theme(self):
        theme = ColorTheme.instance()
        if theme.name == "light":
            theme.use('dark')
            self._theme_button.icon('sun-fill')
        else:
            theme.use('light')
            self._theme_button.icon('moon-fill')


with App("Button Demo", theme="dark") as app:
    app.geometry('800x600')

    with GridBox(columns=["250px", 1], rows=[1], sticky="nsew", expand=True):

        with GridBox(columns=[1], rows=[1, 1], padding=16, surface="background-1", sticky="news"):

            with PackFrame(direction="column", sticky="new", gap=8, sticky_content="ew", expand_content=True):
                Button(text="Button 1", color="secondary")
                Button(text="Button 2", color="secondary")
                Button(text="Button 3", color="secondary")

            with PackFrame(direction="column-reverse", sticky="sew", expand=True, gap=8, sticky_content="ew", expand_content=True):
                Button(text="Light Mode", icon="sun-fill", on_click=lambda: app.theme.use('light'))
                Button(text="Dark Mode", icon="moon-fill", on_click=lambda: app.theme.use('dark'))

        with GridBox(columns=[1, 0], rows=[1], gap=16, padding=16, margin=16, expand=True, surface="background-1", sticky="nsew"):
            Button(text="Content Area", sticky="new")
            Button(text="Side Area", sticky="new")

app.run()