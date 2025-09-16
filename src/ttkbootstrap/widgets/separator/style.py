from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import Element, ElementImage
from ttkbootstrap.style.utils import recolor_image


class SeparatorStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__("TSeparator", **kwargs)
        self.options.set_defaults(color='primary', orient='horizontal')

    def register_style(self):
        ttk_style = self.resolve_name()
        surface = self.theme.color(self.surface())
        color_token = self.options('color')
        orient = self.options('orient')

        if color_token == 'border':
            color = self.theme.border(surface)
        else:
            color = self.theme.color(color_token)

        img = recolor_image(f'separator-{orient}', color)
        sticky = "ew" if orient == "horizontal" else "ns"
        self.create_element(ElementImage(f'{ttk_style}.Separator', img, border=0, sticky=sticky))
        self.style_layout(ttk_style, Element(f'{ttk_style}.Separator', sticky=sticky))
        self.configure(ttk_style, background=surface)
