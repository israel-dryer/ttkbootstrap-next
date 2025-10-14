from ttkbootstrap.style import Element, ElementImage, recolor_image, StyleManager


class ScaleStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        super().__init__("TScale", **kwargs)
        self.options.set_defaults(color='primary', orient='horizontal', variant='default')


@ScaleStyleBuilder.register_variant("default")
def build_default_scale_style(b: ScaleStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    orient = b.options('orient').title()

    # style colors
    background = b.color(b.surface_token)
    foreground = b.on_color(background)
    foreground_disabled = b.disabled("text")
    track_color = b.border(background)
    handle_normal = b.color(b.color_token)
    handle_hover = b.hover(handle_normal)
    handle_pressed = b.active(handle_normal)
    handle_disabled = b.disabled("text")
    track_disabled = b.disabled("background")

    # style images
    handle_normal_img = recolor_image("slider-handle", background, handle_normal)
    handle_hover_img = recolor_image("slider-handle", handle_hover, handle_hover)
    handle_pressed_img = recolor_image("slider-handle-focus", background, handle_normal)
    handle_focus_img = recolor_image("slider-handle-focus", background, handle_pressed)
    handle_disabled_img = recolor_image("slider-handle", handle_disabled, handle_disabled)

    track_normal_img = recolor_image(f"slider-track-{orient}", track_color)
    track_disabled_img = recolor_image(f"slider-track-{orient}", track_disabled)
    sticky = "ew" if orient == "Horizontal" else "ns"
    side = "left" if orient == "Horizontal" else "top"
    padding = (8, 0, -8, 0) if orient == "Horizontal" else (0, 8, 0, -8)

    b.style_create_element(
        ElementImage(f"{ttk_style}.{orient}.Scale.slider", handle_normal_img).state_specs(
            [
                ('disabled', handle_disabled_img),
                ('focus', handle_focus_img),
                ('pressed', handle_pressed_img),
                ('hover', handle_hover_img)
            ]))

    b.style_create_element(
        ElementImage(f"{ttk_style}.{orient}.Scale.trough", track_normal_img, padding=padding, border=4).state_specs(
            [
                ('disabled', track_disabled_img)
            ]))

    b.style_create_layout(
        ttk_style, Element(f"{orient}.Scale.padding", sticky=sticky).children(
            [
                Element(f'{ttk_style}.{orient}.Scale.trough', sticky=sticky),
                Element(f'{ttk_style}.{orient}.Scale.slider', sticky="", side=side)]))

    b.style_configure(ttk_style, background=background, foreground=foreground)
    b.style_map(ttk_style, background=[], foreground=[('disabled', foreground_disabled)])
