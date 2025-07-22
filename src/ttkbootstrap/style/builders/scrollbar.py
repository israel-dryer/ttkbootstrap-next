from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import ElementImage, Element
from ttkbootstrap.style.style import Style
from ttkbootstrap.style.utils import recolor_image


class ScrollbarStyleBuilder(StyleBuilderBase):

    def __init__(self, orient="vertical"):
        super().__init__(f"TScrollbar", orient=orient)

    def orient(self, value=None):
        if value is None:
            return self.options.get('orient') or 'vertical'
        else:
            self.options.update(orient=value)
            return self

    def register_style(self):
        if self.orient() == 'horizontal':
            self.build_horizontal()
        else:
            self.build_vertical()

    def build_horizontal(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        background_color = theme.color(self.surface())
        trough_color = theme.subtle('background', background_color)
        thumb_color = theme.border(background_color)
        thumb_hover = theme.hover(thumb_color)
        thumb_pressed = theme.active(thumb_color)

        # images
        trough_img = recolor_image(f'scrollbar-trough-horizontal', trough_color)
        thumb_normal_img = recolor_image(f'scrollbar-thumb-horizontal-min', thumb_color)
        thumb_hover_img = recolor_image(f'scrollbar-thumb-horizontal-max', thumb_hover)
        thumb_pressed_img = recolor_image(f'scrollbar-thumb-horizontal-max', thumb_pressed)

        # elements
        self.create_element(ElementImage(f"{ttk_style}.Scrollbar.trough", trough_img, border=4))
        self.create_element(
            ElementImage(f'{ttk_style}.Scrollbar.thumb', thumb_normal_img, border=5).state_specs([
                ('pressed', thumb_pressed_img),
                ('hover', thumb_hover_img),
            ])
        )

        self.style_layout(ttk_style, Element(f'{ttk_style}.Scrollbar.trough', sticky="ew").children([
            Element(f'{ttk_style}.Scrollbar.thumb', side="left", expand=True, sticky="ew")
        ]))

        self.configure(ttk_style, background=background_color, padding=0)
        self.map(ttk_style, background=[])

    def build_vertical(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        background_color = theme.color(self.surface())
        trough_color = theme.subtle('background', background_color)
        thumb_color = theme.border(background_color)
        thumb_hover = theme.hover(thumb_color)
        thumb_pressed = theme.active(thumb_color)

        # images
        trough_img = recolor_image(f'scrollbar-trough-vertical', trough_color)
        thumb_normal_img = recolor_image(f'scrollbar-thumb-vertical-min', thumb_color)
        thumb_hover_img = recolor_image(f'scrollbar-thumb-vertical-max', thumb_hover)
        thumb_pressed_img = recolor_image(f'scrollbar-thumb-vertical-max', thumb_pressed)

        # elements
        self.create_element(ElementImage(f"{ttk_style}.Scrollbar.trough", trough_img, border=4))
        self.create_element(
            ElementImage(f'{ttk_style}.Scrollbar.thumb', thumb_normal_img, border=5).state_specs([
                ('pressed', thumb_pressed_img),
                ('hover', thumb_hover_img),
            ])
        )
        self.style_layout(ttk_style, Element(f'{ttk_style}.Scrollbar.trough', sticky="ns").children([
            Element(f'{ttk_style}.Scrollbar.thumb', side="top", expand=True, sticky="ns")
        ]))

        self.configure(ttk_style, background=background_color, padding=0)
        self.map(ttk_style, background=[])
