from ttkbootstrap_next.style import Element, StyleManager


class ScrollbarStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        super().__init__("TScrollbar", **kwargs)
        self.options.set_defaults(orient='vertical', variant='default')


@ScrollbarStyleBuilder.register_variant("default")
def build_default_scrollbar_style(b: ScrollbarStyleBuilder):
    orient = b.options('orient')
    if orient == 'vertical':
        return build_default_vertical(b)
    else:
        return build_default_horizontal(b)


def build_default_horizontal(b: ScrollbarStyleBuilder):
    ttk_style = b.resolve_ttk_name()

    background_color = b.color(b.surface_token)
    trough_color = b.elevate(background_color, 1)
    thumb_color = b.border(background_color)
    thumb_hover = b.hover(thumb_color)
    thumb_pressed = b.active(thumb_color)

    b.style_create_layout(
        ttk_style, Element(f'{ttk_style}.Scrollbar.trough', sticky="ew").children(
            [
                Element(f'{ttk_style}.Scrollbar.thumb', side="left", expand=True, sticky="ew")
            ]))

    b.style_configure(
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
    b.style_map(
        ttk_style,
        background=[('pressed', thumb_pressed), ('hover', thumb_hover)],
        bordercolor=[('active', trough_color), ('hover', trough_color)],
        darkcolor=[('pressed', thumb_pressed), ('hover', thumb_hover)],
        lightcolor=[('pressed', thumb_pressed), ('hover', thumb_hover)],
        troughcolor=[('active', trough_color), ('hover', trough_color)]
    )


def build_default_vertical(b: ScrollbarStyleBuilder):
    ttk_style = b.resolve_ttk_name()

    background_color = b.color(b.surface_token)
    trough_color = b.elevate(background_color, 1)
    thumb_color = b.border(background_color)
    thumb_hover = b.hover(thumb_color)
    thumb_pressed = b.active(thumb_color)

    b.style_create_layout(
        ttk_style, Element(f'{ttk_style}.Scrollbar.trough', sticky="ns").children(
            [
                Element(f'{ttk_style}.Scrollbar.thumb', side="top", expand=True, sticky="ns")
            ]))

    b.style_configure(
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
    b.style_map(
        ttk_style,
        background=[('pressed', thumb_pressed), ('hover', thumb_hover)],
        bordercolor=[('active', trough_color), ('hover', trough_color)],
        darkcolor=[('pressed', thumb_pressed), ('hover', thumb_hover)],
        lightcolor=[('pressed', thumb_pressed), ('hover', thumb_hover)],
        troughcolor=[('active', trough_color), ('hover', trough_color)]
    )
