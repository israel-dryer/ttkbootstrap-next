from tkinter import Menu

from ttkbootstrap_next.style import StyleManager


class NativeMenuStyleBuilder(StyleManager):
    def __init__(self, menu: Menu, **kwargs):
        super().__init__("tkinter", **kwargs)
        self._menu: Menu = menu
        self.options.set_defaults(
            surface="background",
            variant="default",
            active_background="primary",
            select_color="primary"
        )

    @property
    def menu(self) -> Menu:
        return self._menu


@NativeMenuStyleBuilder.register_variant("default")
def build_default_native_menu_style(b: NativeMenuStyleBuilder):
    background = b.color(b.surface_token)
    foreground = b.on_color(background)
    active_background = b.color(b.options("active_background"))
    active_foreground = b.on_color(active_background)
    select_color = b.color(b.options("select_color"))

    b.menu.configure(
        activeborderwidth=0,
        borderwidth=0,
        background=background,
        foreground=foreground,
        activebackground=active_background,
        activeforeground=active_foreground,
        selectcolor=select_color,
        relief='flat',
        tearoff=False,
    )
