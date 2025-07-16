from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import ElementImage, Element
from ttkbootstrap.style.style import Style
from ttkbootstrap.style.utils import recolor_image


class ProgressStyleBuilder(StyleBuilderBase):

    def __init__(self, color: str = "primary", orient="horizontal", variant="default"):
        target = f"{orient.title()}.TProgressbar"
        super().__init__(target, orient=orient, color=color, variant=variant)

    def orient(self, value=None):
        if value is None:
            return self.options.get('orient') or 'horizontal'
        else:
            self._target = f"{value.title()}.TProgressbar"
            self.options.update(orient=value)
            return self

    def color(self, value=None):
        if value is None:
            return self.options.get('color') or 'primary'
        else:
            self.options.update(color=value)
            return self

    def variant(self, value=None):
        if value is None:
            return self.options.get('variant') or 'default'
        else:
            self.options.update(variant=value)
            return self

    def register_style(self):
        self.build_default_progressbar()
        # if self.variant() == "striped":
        #     self.build_striped_progressbar()
        # else:
        #     self.build_default_progressbar()

    def build_default_progressbar(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        orient = self.orient()
        variant = self.variant()

        # style colors
        background = theme.color(self.surface())
        trough_color = theme.border(background)
        trough_disabled = theme.disabled("background")
        bar_color = theme.color(self.color())
        bar_disabled = theme.disabled("text")

        sticky = "ew" if orient == "horizontal" else "ns"
        side = "left" if orient == "horizontal" else "top"

        trough_normal_img = recolor_image(f"progress-trough-{orient}", trough_color)
        trough_disabled_img = recolor_image(f"progress-trough-{orient}", trough_disabled)
        bar_normal_img = recolor_image(f"progress-bar-{orient}-{variant}", background, bar_color)
        bar_disabled_img = recolor_image(f"progress-bar-{orient}-{variant}", background, bar_disabled)
        element_prefix = ttk_style.replace('TProgressbar', 'Progressbar')

        self.create_element(
            ElementImage(
                f"{element_prefix}.trough", trough_normal_img).state_specs([
                ('disabled', trough_disabled_img)
            ]))

        self.create_element(
            ElementImage(f"{element_prefix}.pbar", bar_normal_img).state_specs([
                ('disabled', bar_disabled_img)
            ]))

        self.style_layout(ttk_style,
                          Element(f'{element_prefix}.trough', sticky="nsew").children([
                              Element(f'{element_prefix}.pbar', sticky=sticky, side=side)
                          ]))

        self.configure(ttk_style, background=background)
        self.map(ttk_style, background=[])
