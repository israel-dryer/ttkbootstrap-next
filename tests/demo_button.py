from ttkbootstrap.core import App
from ttkbootstrap.style.theme import ColorTheme
from ttkbootstrap.widgets import CheckButton, GridFrame, IconButton, LabelFrame, RadioButton, Button
from ttkbootstrap.widgets.layout.pack_frame import PackFrame

"""
    - Add a `mount()` function to the layouts
"""

class ButtonFrameSection(LabelFrame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # add children
        with GridFrame(self, cols=4) as grid:
            grid.add(btn := IconButton(icon='moon-fill', variant="ghost", on_click=self.toggle_theme))
            grid.add(IconButton(icon='house-fill', variant="ghost"))
            grid.add(IconButton(icon='bag-check-fill', variant="ghost"))
            grid.add(CheckButton(text='Is Deployed'))
            self._theme_button = btn
            self.add(grid)

    def toggle_theme(self):
        theme = ColorTheme.instance()
        if theme.name == "light":
            theme.use('dark')
            self._theme_button.icon('sun-fill')
        else:
            theme.use('light')
            self._theme_button.icon('moon-fill')


with App("Button Demo") as app:
    with PackFrame(side="top", gap=16) as main:
        main.pack(fill='both', padx=16, pady=16)

        with PackFrame(gap=8, side="top") as f:
            f.add(Button(text="Primary", icon="house-fill"))
            f.add(Button(text="Secondary", icon="house-fill", color="secondary", variant="ghost"))
            main.add(f)

        main.add(ButtonFrameSection(padding=8))

        with PackFrame(gap=8) as rb:
            rb.add(RadioButton(text="Red", color="danger", value="red", group="colors"))
            rb.add(RadioButton(text="Green", color="success", value="green", group="colors"))
            rb.add(RadioButton(text="Blue", color="primary", value="primary", group="colors"))

        main.add_all([rb])


    app.run()
