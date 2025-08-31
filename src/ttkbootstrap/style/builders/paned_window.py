from ttkbootstrap.style.builders.base import StyleBuilderBase


class PanedWindowStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__("TPanedwindow", **kwargs)
        self.options.set_defaults(orient='horizontal')

    def register_style(self):
        ttk_style = self.resolve_name()
        surface = self.theme.color(self.surface())
        sash_token = self.options('sash_color')
        if sash_token is None:
            sash_color = self.theme.border(surface)
        else:
            sash_color = self.theme.color(sash_token)
        sash_thickness = self.options('sash_thickness')
        self.configure(ttk_style, background=sash_color)
        self.configure("Sash", sashthickness=sash_thickness, gripcount=0)
