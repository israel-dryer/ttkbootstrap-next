from collections import namedtuple
from typing import Any, Sequence

from ttkbootstrap.interop.constants import event_subs
from ttkbootstrap.interop.types import Sub

_namedtuple_cache = {}


def dict_to_namedtuple(name: str, dictionary: dict[str, Any]):
    """Convert a dictionary to a namedtuple, caching the structure."""
    key = tuple(dictionary.keys())
    if key not in _namedtuple_cache:
        _namedtuple_cache[key] = namedtuple(name, key)
    return _namedtuple_cache[key](**dictionary)


def get_substring(sublist: list[Sub]) -> str:
    return ' '.join([e.code for e in sublist])


def map_event_data(event_data: Sequence[str], subs: list[Sub]) -> dict[str, Any]:
    out_data = {}
    for i, sub in enumerate(event_data):
        if sub != '??':
            try:
                key = subs[i].name
                val = subs[i].converter(sub)
                if val is not None:
                    out_data[key] = val
            except (TypeError, IndexError):
                continue
    return out_data


def get_event_namedtuple(event_name: str, raw_data: Sequence[str]) -> Any:
    """Create a namedtuple event object from raw event data."""
    event_dict = {'name': event_name}
    event_dict.update(map_event_data(raw_data, event_subs))
    return dict_to_namedtuple('Event', event_dict)
