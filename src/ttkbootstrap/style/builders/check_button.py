from ttkbootstrap.images.utils import create_transparent_image
from ttkbootstrap.style.builders.base import StyleBuilderBase
from ttkbootstrap.style.element import Element, ElementImage
from ttkbootstrap.style.utils import recolor_image


class CheckButtonStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):
        super().__init__('TCheckbutton', **kwargs)
        self.options.setdefault('color', 'primary')

    def register_style(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        background = theme.color(self.surface())
        background_hover = theme.hover(background)
        foreground = theme.on_color(background)
        foreground_disabled = theme.disabled('text')
        normal = theme.color(self.options.get("color"))
        foreground_active = theme.on_color(normal)
        pressed = theme.active(normal)
        hovered = theme.hover(normal)
        border = theme.border(background)
        focus = hovered
        focus_ring = theme.focus_ring(normal, background)
        disabled = theme.disabled()

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
        self.create_element(
            ElementImage(f'{ttk_style}.spacer', spacer_img, sticky="ew"))

        self.create_element(
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

        self.style_layout(
            ttk_style, Element('Checkbutton.padding', sticky="nsew").children(
                [
                    Element(f'{ttk_style}.indicator', side="left", sticky=""),
                    Element(f'{ttk_style}.spacer', side="left"),
                    Element('Checkbutton.label', side="left", sticky="nsew")
                ])
        )

        self.configure(ttk_style, background=background, foreground=foreground)
        self.map(ttk_style, background=[], foreground=[])
