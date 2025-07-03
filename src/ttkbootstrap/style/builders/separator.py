from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import Element, ElementImage
from ttkbootstrap.style.utils import recolor_image


class SeparatorStyleBuilder(StyleBuilderBase):

    def __init__(self, color, orient: str):
        super().__init__("TSeparator", color=color, orient=orient)

    def color(self, value: str = None):
        if value is None:
            return self.options.get('color', 'primary')
        else:
            self.options.update(color=value)
            return self

    def orient(self, value: str = None):
        if value is None:
            return self.options.get('orient', 'horizontal')
        else:
            self.options.update(orient=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        surface = self.theme.surface_color(self.surface())

        if self.color() == 'border':
            color = self.theme.border_on_surface(surface)
        else:
            color = self.theme.color(self.color())

        img = recolor_image(f'separator-{self.orient()}', color)
        sticky = "ew" if self.orient() == "horizontal" else "ns"
        self.create_element(ElementImage(f'{ttk_style}.Separator', img, border=0, sticky=sticky))
        self.style_layout(ttk_style, Element(f'{ttk_style}.Separator', sticky=sticky))
        self.configure(ttk_style, background=surface)
