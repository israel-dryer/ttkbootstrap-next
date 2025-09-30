from ttkbootstrap.images.utils import create_transparent_image
from ttkbootstrap.style import Element, ElementImage, StyleBuilderBase, recolor_image


class RadiobuttonStyleBuilder(StyleBuilderBase):

    def __init__(self, **kwargs):

        super().__init__('TRadiobutton', **kwargs)
        self.options.set_defaults(color='primary', variant='default')

    def register_style(self):
        variant = self.options("variant")
        if variant == 'list':
            self.build_list_style()
        else:
            self.build_default_style()

    def build_list_style(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        color_token = self.options("color")
        background = theme.color(self.surface())
        background_hover = theme.elevate(background, 1)
        background_selected = theme.subtle(color_token, background)
        foreground = theme.on_color(background)
        normal = theme.color(color_token)
        foreground_active = theme.on_color(normal)
        hovered = theme.hover(normal)
        border = theme.border(background)

        # checkbutton element images
        normal_checked_img = recolor_image('radio-selected', foreground_active, normal, background_selected)
        normal_unchecked_img = recolor_image('radio-unselected', background, border, background)

        hovered_checked_img = recolor_image('radio-selected', foreground_active, hovered, background_selected)
        hovered_unchecked_img = recolor_image('radio-unselected', background_hover, border, background_hover)

        spacer_img = create_transparent_image(8, 1)
        self.create_element(
            ElementImage(f'{ttk_style}.spacer', spacer_img, sticky="ew"))

        self.create_element(
            ElementImage(f'{ttk_style}.indicator', normal_unchecked_img, sticky="ns", padding=3).state_specs(
                [
                    # Hover states
                    ('hover selected', hovered_checked_img),
                    ('hover !selected !alternate', hovered_unchecked_img),

                    # Normal base states
                    ('selected', normal_checked_img),
                    ('!selected !alternate', normal_unchecked_img),
                ]
            ))

        self.style_layout(
            ttk_style, Element('Radiobutton.padding', sticky="nsew").children(
                [
                    Element(f'{ttk_style}.indicator', side="left", sticky=""),
                    Element(f'{ttk_style}.spacer', side="left"),
                    Element('Radiobutton.label', side="left", sticky="nsew")
                ])
        )

        self.configure(ttk_style, background=background, foreground=foreground)
        self.map(ttk_style, background=[('selected', background_selected), ('hover', background_hover)], foreground=[])

    def build_default_style(self):
        ttk_style = self.resolve_name()
        theme = self.theme
        background = theme.color(self.surface())
        background_hover = theme.hover(background)
        foreground = theme.on_color(background)
        foreground_disabled = theme.disabled('text')
        normal = theme.color(self.options('color'))
        foreground_active = theme.on_color(normal)
        pressed = theme.active(normal)
        hovered = theme.hover(normal)
        border = theme.border(background)
        focus = hovered
        focus_ring = theme.focus_ring(normal, background)
        disabled = theme.disabled()

        # checkbutton element images
        normal_checked_img = recolor_image('radio-selected', foreground_active, normal, background)
        normal_unchecked_img = recolor_image('radio-unselected', background, border, background)

        hovered_checked_img = recolor_image('radio-selected', foreground_active, hovered, background)
        hovered_unchecked_img = recolor_image('radio-unselected', background_hover, border, background)

        pressed_checked_img = recolor_image('radio-selected', foreground_active, pressed, background)
        pressed_unchecked_img = recolor_image('radio-unselected', background_hover, pressed, background)

        focus_checked_img = recolor_image('radio-selected', foreground_active, focus, focus_ring)
        focus_unchecked_img = recolor_image('radio-unselected', background_hover, focus, focus_ring)

        disabled_checked_img = recolor_image('radio-selected', disabled, foreground_disabled, background)
        disabled_unchecked_img = recolor_image('radio-unselected', foreground_disabled, foreground_disabled, background)

        spacer_img = create_transparent_image(8, 1)
        self.create_element(
            ElementImage(f'{ttk_style}.spacer', spacer_img, sticky="ew"))

        self.create_element(
            ElementImage(f'{ttk_style}.indicator', normal_unchecked_img, sticky="ns", padding=3).state_specs(
                [
                    # Disabled states
                    ('disabled selected', disabled_checked_img),
                    ('disabled !selected !alternate', disabled_unchecked_img),

                    # Focused states
                    ('focus selected', focus_checked_img),
                    ('focus !selected !alternate', focus_unchecked_img),

                    # Pressed states
                    ('pressed selected', pressed_checked_img),
                    ('pressed !selected !alternate', pressed_unchecked_img),

                    # Hover states
                    ('hover selected', hovered_checked_img),
                    ('hover !selected !alternate', hovered_unchecked_img),

                    # Normal base states
                    ('selected', normal_checked_img),
                    ('!selected !alternate', normal_unchecked_img),
                ]
            ))

        self.style_layout(
            ttk_style, Element('Radiobutton.padding', sticky="nsew").children(
                [
                    Element(f'{ttk_style}.indicator', side="left", sticky=""),
                    Element(f'{ttk_style}.spacer', side="left"),
                    Element('Radiobutton.label', side="left", sticky="nsew")
                ])
        )

        self.configure(ttk_style, background=background, foreground=foreground)
        self.map(ttk_style, background=[], foreground=[])
