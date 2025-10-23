from ttkbootstrap.style import Element, ElementImage, StyleManager, recolor_image


class ButtonStyleBuilder(StyleManager):

    def __init__(self, **kwargs):
        super().__init__("TButton", **kwargs)
        self.options.set_defaults(
            color='primary',
            variant='solid',
            size='md',
            icon_only=False,
            select_background='primary'
        )


@ButtonStyleBuilder.register_variant("solid")
def build_solid_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    normal = b.color(b.color_token)
    foreground = b.on_color(normal)
    foreground_disabled = b.disabled("text")
    pressed = b.active(normal)
    hovered = b.hover(normal)
    focused = hovered
    focused_border = b.focus_border(normal)
    disabled = b.disabled()
    focused_ring = b.focus_ring(normal, surface)

    # button element images
    normal_img = recolor_image(f'button', normal, normal, surface)
    pressed_img = recolor_image(f'button', pressed, pressed, surface)
    hovered_img = recolor_image(f'button', hovered, hovered, surface)
    focused_img = recolor_image(f'button', focused, focused_border, focused_ring)
    focused_hovered_img = recolor_image(f'button', hovered, focused_border, focused_ring)
    focused_pressed_img = recolor_image(f'button', pressed, focused_border, focused_ring)
    disabled_img = recolor_image(f'button', disabled, disabled, surface, surface)
    btn_padding = button_img_border(b.options('size'))

    # button element
    b.style_create_element(
        ElementImage(
            f'{ttk_style}.border', normal_img, sticky="nsew", border=btn_padding, padding=btn_padding).state_specs(
            [
                ('disabled', disabled_img),
                ('focus pressed', focused_pressed_img),
                ('focus hover', focused_hovered_img),
                ('focus', focused_img),
                ('pressed', pressed_img),
                ('hover', hovered_img),
            ]))

    create_button_style(b)

    b.style_configure(
        ttk_style,
        background=surface,
        foreground=foreground,
        stipple="gray12",
        relief='flat',
        padding=0,
        font=b.get_font(b.options('size')))

    b.style_map(ttk_style, foreground=[('disabled', foreground_disabled)], background=[('disabled', disabled)])


@ButtonStyleBuilder.register_variant("outline")
def build_outline_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    foreground = b.color(b.color_token)
    foreground_disabled = b.disabled("text")
    foreground_active = b.on_color(foreground)
    normal = surface
    disabled = foreground_disabled
    pressed = b.hover(foreground)
    focused = hovered = pressed
    focused_border = b.focus_border(foreground)
    focused_ring = b.focus_ring(foreground, surface)

    # button element images
    normal_img = recolor_image(f'button', normal, foreground, surface)
    pressed_img = recolor_image(f'button', pressed, pressed, surface)
    hovered_img = recolor_image(f'button', hovered, hovered, surface)
    focused_img = recolor_image(f'button', focused, focused_border, focused_ring)
    focused_hovered_img = recolor_image(f'button', hovered, focused_border, focused_ring)
    focused_pressed_img = recolor_image(f'button', pressed, focused_border, focused_ring)
    disabled_img = recolor_image(f'button', surface, disabled, surface, surface)
    btn_padding = button_img_border(b.options('size'))

    # button element
    b.style_create_element(
        ElementImage(
            f'{ttk_style}.border', normal_img, sticky="nsew", border=btn_padding, padding=btn_padding).state_specs(
            [
                ('disabled', disabled_img),
                ('focus pressed', focused_pressed_img),
                ('focus hover', focused_hovered_img),
                ('focus', focused_img),
                ('pressed', pressed_img),
                ('hover', hovered_img),
            ]))

    create_button_style(b)
    b.style_configure(
        ttk_style,
        background=surface,
        foreground=foreground,
        relief='flat',
        stipple="gray12",
        padding=0,
        font=b.get_font(b.options('size')))

    b.style_map(
        ttk_style,
        foreground=[
            ('disabled', foreground_disabled),
            ('focus', foreground_active),
            ('hover', foreground_active),
        ], background=[('disabled', surface)])


@ButtonStyleBuilder.register_variant("ghost")
def build_ghost_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    foreground = b.color(b.color_token)
    foreground_disabled = b.disabled("text")
    normal = surface
    pressed = b.subtle(b.color_token, surface)
    focused = hovered = pressed
    focused_ring = b.focus_ring(focused, surface)

    # button element images
    normal_img = recolor_image(f'button', normal, normal, surface, surface)
    pressed_img = recolor_image(f'button', pressed, surface, surface, surface)
    hovered_img = recolor_image(f'button', hovered, surface, surface, surface)
    focused_img = recolor_image(f'button', focused, focused, focused_ring, surface)
    focused_hovered_img = recolor_image(f'button', hovered, focused, focused_ring, surface)
    focused_pressed_img = recolor_image(f'button', pressed, focused, focused_ring, surface)
    disabled_img = recolor_image(f'button', surface, surface, surface, surface)
    btn_padding = button_img_border(b.options('size'))

    # button element
    b.style_create_element(
        ElementImage(
            f'{ttk_style}.border', normal_img, sticky="nsew", border=btn_padding,
            padding=btn_padding).state_specs(
            [
                ('disabled', disabled_img),
                ('focus pressed', focused_pressed_img),
                ('focus hover', focused_hovered_img),
                ('focus', focused_img),
                ('pressed', pressed_img),
                ('hover', hovered_img),
            ]))

    create_button_style(b)
    b.style_configure(
        ttk_style,
        background=surface,
        foreground=foreground,
        relief='flat',
        stipple="gray12",
        padding=0,
        font=b.get_font(b.options('size')))

    b.style_map(
        ttk_style,
        foreground=[('disabled', foreground_disabled)],
        background=[('disabled', surface)])


@ButtonStyleBuilder.register_variant("text")
def build_text_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    foreground = b.color(b.color_token)
    foreground_disabled = b.disabled("text")

    b.style_create_layout(
        ttk_style, Element('Label.border', sticky="nsew").children(
            [
                Element('Label.padding', sticky="nsew").children(
                    [
                        Element("Label.label", sticky="")
                    ])
            ]))

    b.style_configure(
        ttk_style,
        background=surface,
        foreground=foreground,
        relief='flat',
        stipple="gray12",
        padding=0,
        font=b.get_font(b.options('size')))
    b.style_map(ttk_style, foreground=[('disabled', foreground_disabled)], background=[])


@ButtonStyleBuilder.register_variant("prefix")
@ButtonStyleBuilder.register_variant("suffix")
def build_addon_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    border = b.border(surface)
    foreground = b.on_color(surface)
    foreground_disabled = b.disabled("text")
    normal = b.disabled()
    pressed = b.subtle('secondary', surface)
    focused = hovered = pressed

    # button element images
    normal_img = recolor_image(f'input-{b.variant}', normal, border)
    pressed_img = recolor_image(f'input-{b.variant}', pressed, border, surface, surface)
    hovered_img = recolor_image(f'input-{b.variant}', hovered, border, surface, surface)
    focused_img = recolor_image(f'input-{b.variant}', focused, border, focused, surface)
    focused_hovered_img = recolor_image(f'input-{b.variant}', hovered, border, focused, surface)
    focused_pressed_img = recolor_image(f'input-{b.variant}', pressed, border, focused, surface)
    disabled_img = recolor_image(f'input-{b.variant}', normal, border, surface, surface)
    btn_padding = button_img_border(b.options("size"))

    # button element
    b.style_create_element(
        ElementImage(
            f'{ttk_style}.border', normal_img, sticky="nsew", border=btn_padding,
            padding=btn_padding).state_specs(
            [
                ('disabled', disabled_img),
                ('focus pressed', focused_pressed_img),
                ('focus hover', focused_hovered_img),
                ('focus', focused_img),
                ('pressed', pressed_img),
                ('hover', hovered_img),
            ]))

    create_button_style(b)
    b.style_configure(
        ttk_style,
        background=surface,
        foreground=foreground,
        relief='flat',
        stipple="gray12",
        padding=0,
        font=b.get_font(b.options('size')))

    b.style_map(
        ttk_style,
        foreground=[('disabled', foreground_disabled)],
        background=[('disabled', surface)])


@ButtonStyleBuilder.register_variant("menu-item")
def build_menu_item_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    background_hover = b.elevate(surface, 1)
    background_pressed = b.elevate(surface, 2)

    # button element
    b.style_create_layout(
        ttk_style, Element('Label.border', sticky="nsew").children(
            [
                Element('Label.padding', sticky="nsew").children(
                    [
                        Element("Label.label", sticky="")
                    ])
            ]))

    b.style_configure(
        ttk_style,
        background=surface,
        padding=0,
        relief='flat',
        stipple="gray12",
        font=b.get_font(b.options('size')))

    b.style_map(
        ttk_style,
        foreground=[],
        background=[
            ('pressed', background_pressed),
            ('hover', background_hover)])


@ButtonStyleBuilder.register_variant("list")
def build_list_button_style(b: ButtonStyleBuilder):
    b.build_icon_assets()
    ttk_style = b.resolve_ttk_name()

    surface = b.color(b.surface_token)
    background_hover = b.elevate(surface, 1)
    background_pressed = b.elevate(surface, 2)
    background_selected = b.color(b.options('select_background'))
    background_selected_hover = b.hover(background_selected)

    # button element
    b.style_create_layout(
        ttk_style, Element('Label.border', sticky="nsew").children(
            [
                Element('Label.padding', sticky="nsew").children(
                    [
                        Element("Label.label", sticky="")
                    ])
            ]))

    b.style_configure(
        ttk_style,
        background=surface,
        padding=0,
        relief='flat',
        stipple="gray12",
        font=b.get_font(b.options('size')))

    b.style_map(
        ttk_style,
        foreground=[],
        background=[
            ('focus selected', background_selected_hover),
            ('selected hover', background_selected_hover),
            ('selected', background_selected),
            ('pressed', background_pressed),
            ('hover', background_hover),
            ('focus', background_hover)])


# ----- Helpers -----

def button_img_border(size: str):
    if size == "sm":
        return 6
    elif size == "md":
        return 8
    else:
        return 10


# ----- Icon Builders -----


@ButtonStyleBuilder.register_variant("text-icon-builder")
def build_text_icon_assets(b: ButtonStyleBuilder, icon):
    surface = b.color(b.surface_token)
    foreground = b.on_color(surface)
    foreground_disabled = b.disabled("text")
    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'focus', foreground)
    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.map_stateful_icons()


@ButtonStyleBuilder.register_variant("solid-icon-builder")
def build_solid_icon_assets(b: ButtonStyleBuilder, icon: dict):
    background = b.color(b.color_token)
    foreground = b.on_color(background)
    foreground_disabled = b.disabled("text")

    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'focus', foreground)
    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.map_stateful_icons()


@ButtonStyleBuilder.register_variant("outline-icon-builder")
def build_outline_icon_assets(b: ButtonStyleBuilder, icon: dict):
    accent = b.color(b.color_token)
    foreground_active = b.on_color(accent)
    foreground_disabled = b.disabled("text")
    b.register_stateful_icon(icon, 'normal', accent)
    b.register_stateful_icon(icon, 'hover', foreground_active)
    b.register_stateful_icon(icon, 'pressed', foreground_active)
    b.register_stateful_icon(icon, 'focus', foreground_active)
    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.map_stateful_icons()


@ButtonStyleBuilder.register_variant("ghost-icon-builder")
def build_ghost_icon_assets(b: ButtonStyleBuilder, icon: dict):
    foreground = b.color(b.color_token)
    foreground_disabled = b.disabled("text")
    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'focus', foreground)
    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.map_stateful_icons()


@ButtonStyleBuilder.register_variant("prefix-icon-builder")
@ButtonStyleBuilder.register_variant("suffix-icon-builder")
def build_addon_icon_assets(b: ButtonStyleBuilder, icon: dict):
    """Create stateful icons for addon variant"""
    surface = b.color(b.surface_token)
    foreground = b.on_color(surface)
    foreground_disabled = b.disabled("text")
    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'focus', foreground)
    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.map_stateful_icons()


@ButtonStyleBuilder.register_variant("menu-item-icon-builder")
def build_menu_icon_assets(b: ButtonStyleBuilder, icon: dict):
    """Create stateful icons for menu item variant"""
    icon['size'] = 14
    background = b.color(b.surface_token)
    foreground = b.on_color(background)
    foreground_disabled = b.disabled("text")

    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'selected', foreground)
    b.map_stateful_icons()


@ButtonStyleBuilder.register_variant("list-icon-builder")
def build_list_icon_assets(b: ButtonStyleBuilder, icon: dict):
    """Create stateful icons for list variant"""
    icon['size'] = 14
    background = b.color(b.surface_token)
    background_selected = b.color(b.options('select_background'))
    foreground = b.on_color(background)
    foreground_selected = b.on_color(background_selected)
    foreground_disabled = b.disabled("text")

    b.register_stateful_icon(icon, 'disabled', foreground_disabled)
    b.register_stateful_icon(icon, 'normal', foreground)
    b.register_stateful_icon(icon, 'hover', foreground)
    b.register_stateful_icon(icon, 'pressed', foreground)
    b.register_stateful_icon(icon, 'focus', foreground)
    b.register_stateful_icon(icon, 'selected', foreground_selected)
    b.map_stateful_icons()


# ------ Helper to build button style ------

def create_button_style(b: ButtonStyleBuilder):
    """Create a button layout common to all style variants"""
    ttk_style = b.resolve_ttk_name()
    b.style_create_layout(
        ttk_style, Element(f"{ttk_style}.border", sticky="nsew").children(
            [
                Element("Button.padding", sticky="nsew").children(
                    [
                        Element("Button.label", sticky="")
                    ])
            ]))
