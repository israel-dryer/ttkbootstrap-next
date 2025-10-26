from ttkbootstrap_next.style import Element, ElementImage, recolor_image, StyleManager


class EntryStyleBuilder(StyleManager):
    def __init__(self, **kwargs):
        super().__init__("TEntry", **kwargs)
        self.options.set_defaults(variant="default")


@EntryStyleBuilder.register_variant("default")
def build_default_entry_style(b: EntryStyleBuilder):
    ttk_style = b.resolve_ttk_name()
    surface = b.color("background")  # always use the theme background
    disabled_bg = b.disabled('background')
    disabled_fg = b.disabled('text')
    foreground = b.on_color(surface)

    normal_img = recolor_image(f'input-inner', surface)
    b.style_create_element(ElementImage(f'{ttk_style}.field', normal_img, sticky="nsew"))
    b.style_create_layout(
        ttk_style, Element(f'{ttk_style}.field').children(
            [
                Element('Entry.padding', sticky="ew").children(
                    [
                        Element('Entry.textarea', sticky="nsew")
                    ])
            ]))

    b.style_configure(
        ttk_style,
        relief='flat',
        foreground=foreground,
        background=surface,
        fieldbackground=surface,
        selectborderwidth=0,
        bordercolor=surface,
        darkcolor=surface,
        lightcolor=surface,
        insertcolor=foreground,
        padding=(8, 0),
        selectforeground=b.on_color(b.color('primary')),
        selectbackground=b.color('primary')
    )

    b.style_map(
        ttk_style,
        background=[('disabled', disabled_bg)],
        fieldbackground=[('disabled', disabled_bg)],
        selectforeground=[],
        selectbackground=[],
        bordercolor=[('disabled', disabled_bg)],
        darkcolor=[('disabled', disabled_bg)],
        lightcolor=[('disabled', disabled_bg)],
        foreground=[('disabled !readonly', disabled_fg)]
    )
