from ttkbootstrap_next.style import Element, ElementImage, recolor_image, StyleManager


class ProgressbarStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        target = f"{kwargs.get('orient', 'horizontal').title()}.TProgressbar"
        super().__init__(target, **kwargs)
        self.options.set_defaults(variant='default', color='primary', orient='horizontal')


@ProgressbarStyleBuilder.register_variant("default")
@ProgressbarStyleBuilder.register_variant("striped")
def build_default_progressbar_style(b: ProgressbarStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    orient = b.options('orient')

    # style colors
    background = b.color(b.surface_token)
    trough_color = b.border(background)
    trough_disabled = b.disabled("background")
    bar_color = b.color(b.options("color"))
    bar_disabled = b.disabled("text")

    sticky = "ew" if orient == "horizontal" else "ns"
    side = "left" if orient == "horizontal" else "top"

    trough_normal_img = recolor_image(f"progress-trough-{orient}", trough_color)
    trough_disabled_img = recolor_image(f"progress-trough-{orient}", trough_disabled)
    bar_normal_img = recolor_image(f"progress-bar-{orient}-{b.variant}", background, bar_color)
    bar_disabled_img = recolor_image(f"progress-bar-{orient}-{b.variant}", background, bar_disabled)
    element_prefix = ttk_style.replace('TProgressbar', 'Progressbar')

    b.style_create_element(
        ElementImage(
            f"{element_prefix}.trough", trough_normal_img).state_specs(
            [
                ('disabled', trough_disabled_img)
            ]))

    b.style_create_element(
        ElementImage(f"{element_prefix}.pbar", bar_normal_img).state_specs(
            [
                ('disabled', bar_disabled_img)
            ]))

    b.style_create_layout(
        ttk_style,
        Element(f'{element_prefix}.trough', sticky="nsew").children(
            [
                Element(f'{element_prefix}.pbar', sticky=sticky, side=side)
            ]))

    b.style_configure(ttk_style, background=background)
    b.style_map(ttk_style, background=[])
