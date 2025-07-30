from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import Element


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
        trough_color = theme.elevate(background_color, 1)
        thumb_color = theme.border(background_color)
        thumb_hover = theme.hover(thumb_color)
        thumb_pressed = theme.active(thumb_color)

        self.style_layout(ttk_style, Element(f'{ttk_style}.Scrollbar.trough', sticky="ew").children([
            Element(f'{ttk_style}.Scrollbar.thumb', side="left", expand=True, sticky="ew")
        ]))

        self.configure(
            ttk_style,
            background=thumb_color,
            troughcolor=background_color,
            padding=0,
            bordercolor=background_color,
            darkcolor=thumb_color,
            lightcolor=thumb_color,
            gripcount=0,
            relief='flat',
            arrowsize=12,
        )
        self.map(
            ttk_style,
            background=[('pressed', thumb_pressed), ('hover', thumb_hover)],
            bordercolor=[('active', trough_color), ('hover', trough_color)],
            darkcolor=[('pressed', thumb_pressed), ('hover', thumb_hover)],
            lightcolor=[('pressed', thumb_pressed), ('hover', thumb_hover)],
            troughcolor=[('active', trough_color), ('hover', trough_color)]
        )

    def build_vertical(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        background_color = theme.color(self.surface())
        trough_color = theme.elevate(background_color, 1)
        thumb_color = theme.border(background_color)
        thumb_hover = theme.hover(thumb_color)
        thumb_pressed = theme.active(thumb_color)

        self.style_layout(ttk_style, Element(f'{ttk_style}.Scrollbar.trough', sticky="ns").children([
            Element(f'{ttk_style}.Scrollbar.thumb', side="top", expand=True, sticky="ns")
        ]))

        self.configure(
            ttk_style,
            background=thumb_color,
            troughcolor=background_color,
            padding=0,
            bordercolor=background_color,
            darkcolor=thumb_color,
            lightcolor=thumb_color,
            gripcount=0,
            relief='flat',
            arrowsize=12,
        )
        self.map(
            ttk_style,
            background=[('pressed', thumb_pressed), ('hover', thumb_hover)],
            bordercolor=[('active', trough_color), ('hover', trough_color)],
            darkcolor=[('pressed', thumb_pressed), ('hover', thumb_hover)],
            lightcolor=[('pressed', thumb_pressed), ('hover', thumb_hover)],
            troughcolor=[('active', trough_color), ('hover', trough_color)]
        )
