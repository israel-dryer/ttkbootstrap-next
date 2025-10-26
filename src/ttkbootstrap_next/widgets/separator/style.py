from ttkbootstrap_next.style import Element, ElementImage, recolor_image, StyleManager


class SeparatorStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        super().__init__("TSeparator", **kwargs)
        self.options.set_defaults(color="primary", orient="horizontal", variant="default")


@SeparatorStyleBuilder.register_variant("default")
def build_default_separator_style(b: SeparatorStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    surface = b.color(b.surface_token)
    orient = b.options('orient')

    if b.color_token == 'border':
        color = b.border(surface)
    else:
        color = b.color(b.color_token)

    img = recolor_image(f'separator-{orient}', color)
    sticky = "ew" if orient == "horizontal" else "ns"
    b.style_create_element(ElementImage(f'{ttk_style}.Separator', img, border=0, sticky=sticky))
    b.style_create_layout(ttk_style, Element(f'{ttk_style}.Separator', sticky=sticky))
    b.style_configure(ttk_style, background=surface)
