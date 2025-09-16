from ttkbootstrap.style import StyleBuilderBase, Element, ElementImage, recolor_image


class ScaleStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__("TScale", **kwargs)
        self.options.set_defaults(color='primary', orient='horizontal')

    def register_style(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        orient = self.options('orient').title()

        # style colors
        background = theme.color(self.surface())
        foreground = theme.on_color(background)
        foreground_disabled = theme.disabled("text")
        track_color = theme.border(background)
        handle_normal = theme.color(self.options('color'))
        handle_hover = theme.hover(handle_normal)
        handle_pressed = theme.active(handle_normal)
        handle_disabled = theme.disabled("text")
        track_disabled = theme.disabled("background")

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

        self.create_element(
            ElementImage(f"{ttk_style}.{orient}.Scale.slider", handle_normal_img).state_specs(
                [
                    ('disabled', handle_disabled_img),
                    ('focus', handle_focus_img),
                    ('pressed', handle_pressed_img),
                    ('hover', handle_hover_img)
                ]))

        self.create_element(
            ElementImage(f"{ttk_style}.{orient}.Scale.trough", track_normal_img, padding=padding, border=4).state_specs(
                [
                    ('disabled', track_disabled_img)
                ]))

        self.style_layout(
            ttk_style, Element(f"{orient}.Scale.padding", sticky=sticky).children(
                [
                    Element(f'{ttk_style}.{orient}.Scale.trough', sticky=sticky),
                    Element(f'{ttk_style}.{orient}.Scale.slider', sticky="", side=side)]))

        self.configure(ttk_style, background=background, foreground=foreground)
        self.map(ttk_style, background=[], foreground=[('disabled', foreground_disabled)])
