from ttkbootstrap.images.utils import create_transparent_image
from ttkbootstrap.style import Element, ElementImage, StyleManager, recolor_image


class CheckbuttonStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        super().__init__("TCheckbutton", **kwargs)
        self.options.set_defaults(color="primary", variant="default")


@CheckbuttonStyleBuilder.register_variant("default")
def build_default_checkbutton_style(b: CheckbuttonStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    background = b.color(b.surface_token)
    background_hover = b.hover(background)
    foreground = b.on_color(background)
    foreground_disabled = b.disabled('text')
    normal = b.color(b.options("color"))
    foreground_active = b.on_color(normal)
    pressed = b.active(normal)
    hovered = b.hover(normal)
    border = b.border(background)
    focus = hovered
    focus_ring = b.focus_ring(normal, background)
    disabled = b.disabled()

    # checkbutton element images
    normal_checked_img = recolor_image('checkbox-checked', foreground_active, normal, background)
    normal_unchecked_img = recolor_image('checkbox-unchecked', background, border, background)
    normal_indeterminate_img = recolor_image('checkbox-indeterminate', foreground_active, normal, background)

    hovered_checked_img = recolor_image('checkbox-checked', foreground_active, hovered, background)
    hovered_unchecked_img = recolor_image('checkbox-unchecked', background_hover, border, background)
    hovered_indeterminate_img = recolor_image('checkbox-indeterminate', foreground_active, hovered, background)

    pressed_checked_img = recolor_image('checkbox-checked', foreground_active, pressed, background)
    pressed_unchecked_img = recolor_image('checkbox-unchecked', background_hover, pressed, background)
    pressed_indeterminate_img = recolor_image('checkbox-indeterminate', foreground_active, pressed, background)

    focus_checked_img = recolor_image('checkbox-checked', foreground_active, focus, focus_ring)
    focus_unchecked_img = recolor_image('checkbox-unchecked', background_hover, focus, focus_ring)
    focus_indeterminate_img = recolor_image('checkbox-indeterminate', foreground_active, focus, focus_ring)

    disabled_checked_img = recolor_image('checkbox-checked', disabled, foreground_disabled, background)
    disabled_unchecked_img = recolor_image(
        'checkbox-unchecked', foreground_disabled, foreground_disabled, background)
    disabled_indeterminate_img = recolor_image('checkbox-indeterminate', disabled, foreground_disabled, background)

    spacer_img = create_transparent_image(8, 1)
    b.style_create_element(
        ElementImage(f'{ttk_style}.spacer', spacer_img, sticky="ew"))

    b.style_create_element(
        ElementImage(f'{ttk_style}.indicator', normal_unchecked_img, sticky="ns", padding=3).state_specs(
            [
                # Disabled states
                ('disabled alternate !selected', disabled_indeterminate_img),
                ('disabled selected', disabled_checked_img),
                ('disabled !selected !alternate', disabled_unchecked_img),

                # Focused states
                ('focus alternate !selected', focus_indeterminate_img),
                ('focus selected', focus_checked_img),
                ('focus !selected !alternate', focus_unchecked_img),

                # Pressed states
                ('pressed alternate !selected', pressed_indeterminate_img),
                ('pressed selected', pressed_checked_img),
                ('pressed !selected !alternate', pressed_unchecked_img),

                # Hover states
                ('hover alternate !selected', hovered_indeterminate_img),
                ('hover selected', hovered_checked_img),
                ('hover !selected !alternate', hovered_unchecked_img),

                # Normal base states
                ('alternate !selected', normal_indeterminate_img),
                ('selected', normal_checked_img),
                ('!selected !alternate', normal_unchecked_img),
            ]
        ))

    b.style_create_layout(
        ttk_style, Element('Checkbutton.padding', sticky="nsew").children(
            [
                Element(f'{ttk_style}.indicator', side="left", sticky=""),
                Element(f'{ttk_style}.spacer', side="left"),
                Element('Checkbutton.label', side="left", sticky="nsew")
            ])
    )

    b.style_configure(ttk_style, background=background, foreground=foreground)
    b.style_map(ttk_style, background=[], foreground=[])
