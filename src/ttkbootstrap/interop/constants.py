from ttkbootstrap.interop.converters import (
    convert_event_data, convert_event_state, convert_event_timestamp,
    convert_event_type,
    convert_event_widget
)
from ttkbootstrap.interop.types import Sub

event_subs: list[Sub] = [
    # Input
    Sub('type', '%T', convert_event_type),
    Sub('keysym', '%K', str),
    Sub('char', '%A', str),
    Sub('state', '%s', convert_event_state),
    Sub('delta', '%D', float),

    # Position
    Sub('x', '%x', int),
    Sub('y', '%y', int),
    Sub('x_root', '%X', int),
    Sub('y_root', '%Y', int),

    # Geometry
    Sub('width', '%w', int),
    Sub('height', '%h', int),
    Sub('border_width', '%B', int),

    # Windowing
    Sub('window', '%i', hex),
    Sub('subwindow', '%S', hex),
    Sub('send_event', '%E', hex),
    Sub('override_redirect', '%o', str),
    Sub('focus', '%f', int),

    # Metadata
    Sub('time', '[clock seconds]', convert_event_timestamp),
    Sub('mode', '%m', str),
    Sub('place', '%p', str),
    Sub('property', '%P', str),

    # Widget references
    Sub('root', '%R', convert_event_widget),
    Sub('widget', '%W', convert_event_widget),

    # Custom
    Sub('data', '%d', convert_event_data),
]
validation_subs: list[Sub] = [
    Sub('action_type', '%d', int),
    Sub('char_index', '%i', int),
    Sub('validation_value', '%P', str),
    Sub('current_value', '%s', str),
    Sub('insert_value', '%S', str),
    Sub('state', '%v', str),
    Sub('condition', '%V', str),
    Sub('widget', '%W', convert_event_widget)
]
