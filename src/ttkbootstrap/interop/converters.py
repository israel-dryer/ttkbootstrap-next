import json
from datetime import datetime
from json import JSONDecodeError

from ttkbootstrap.interop.events import EventEnum


def convert_event_timestamp(seconds):
    return datetime.fromtimestamp(int(seconds))


def convert_event_state(state):
    try:
        return int(state)
    except (TypeError, ValueError):
        return state


def convert_event_data(data):
    try:
        return json.loads(data)
    except JSONDecodeError:
        return data


def convert_event_type(type_code):
    return EventEnum(int(type_code))


def convert_event_widget(name):
    return name  # Can be extended to resolve widget references
