from ttkbootstrap.core.libtypes import Orient
from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.tokens import ForegroundColor


class PanedWindowStyleBuilder(StyleBuilderBase):

    def __init__(
            self,
            sash_color: ForegroundColor = None,
            sash_thickness: int = None,
            orient: Orient = "horizontal"):
        super().__init__(
            "TPanedwindow",
            sash_color=sash_color,
            sash_thickness=sash_thickness,
            orient=orient
        )

    def sash_color(self, value: str = None):
        if value is None:
            return self.options.get('sash_color', None)
        else:
            self.options.update(sash_color=value)
            return self

    def sash_thickness(self, value: int = None):
        if value is None:
            return self.options.get('sash_thickness', None)
        else:
            self.options.update(sash_thickness=value)
            return self

    def surface(self, value: str = None):
        if value is None:
            return self._surface
        else:
            self._surface = value
            return self

    def orient(self, value: Orient = None):
        if value is None:
            return self.options.get('orient')
        else:
            self.options.update(orient=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        surface = self.theme.color(self.surface())
        sash_token = self.sash_color()
        if sash_token is None:
            sash_color = self.theme.border(surface)
        else:
            sash_color = self.theme.color(sash_token)
        sash_thickness = self.sash_thickness()
        self.configure(ttk_style, background=sash_color)
        self.configure("Sash", sashthickness=sash_thickness, gripcount=0)
