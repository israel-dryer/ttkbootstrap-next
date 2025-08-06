from ttkbootstrap.common.types import Orient
from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import ElementImage, Element
from ttkbootstrap.style.utils import recolor_image


class ScaleStyleBuilder(StyleBuilderBase):

    def __init__(self, color: str = "primary", orient: Orient = "horizontal"):
        super().__init__("TScale", color=color, orient=orient)

    def color(self, value: str = None):
        if value is None:
            return self.options.get('color') or 'primary'
        else:
            self.options.update(color=value)
            return self

    def orient(self, value: Orient = None):
        if value is None:
            return self.options.get('orient') or 'horizontal'
        else:
            self.options.update(orient=value)
            return self

    def register_style(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        orient = self.orient().title()

        # style colors
        background = theme.color(self.surface())
        foreground = theme.on_color(background)
        foreground_disabled = theme.disabled("text")
        track_color = theme.border(background)
        handle_normal = theme.color(self.color())
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

        self.create_element(ElementImage(f"{ttk_style}.{orient}.Scale.slider", handle_normal_img).state_specs([
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

        self.style_layout(ttk_style, Element(f"{orient}.Scale.padding", sticky=sticky).children([
            Element(f'{ttk_style}.{orient}.Scale.trough', sticky=sticky),
            Element(f'{ttk_style}.{orient}.Scale.slider', sticky="", side=side)]))

        self.configure(ttk_style, background=background, foreground=foreground)
        self.map(ttk_style, background=[], foreground=[('disabled', foreground_disabled)])
