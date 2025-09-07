"""
interop.runtime.utils
---------------------

Helpers for converting raw Tk event substrings into structured event payloads.

Workflow:
1. Raw event data arrives from Tcl/Tk as a sequence of strings.
2. `map_event_data` uses the `Sub` spec (from interop.spec.constants) to
   convert each substring into a typed Python value.
3. `_post_process` attaches derived fields such as `mods` (decoded modifiers)
   and `press` (canonical keypress).
4. Sub-payload builders (`get_input_subs`, `get_geometry_subs`, etc.) wrap
   groups of related fields into typed dataclasses, then prune them into
   NamedNamespaces.
5. `get_event_namedtuple` ties everything together, returning a pruned
   `UIEvent` payload ready for logging or emission.

The module also provides a tiny cache-backed helper for converting
dicts into namedtuples (`dict_to_namedtuple`).
"""

from collections import namedtuple
from typing import Any, Sequence

from ttkbootstrap.interop.spec.subs import Sub, event_subs

_namedtuple_cache: dict[tuple[str, ...], Any] = {}


def dict_to_namedtuple(name: str, dictionary: dict[str, Any]) -> Any:
    """Convert a dict into a cached namedtuple."""
    key = tuple(dictionary.keys())
    if key not in _namedtuple_cache:
        _namedtuple_cache[key] = namedtuple(name, key)
    return _namedtuple_cache[key](**dictionary)


def get_substring(sublist: list[Sub]) -> str:
    """Join Sub codes into a space-delimited string."""
    return " ".join([e.code for e in sublist])


def map_event_data(event_data: Sequence[str], subs: list[Sub]) -> dict[str, Any]:
    """Map raw substrings to typed values via Sub converters."""
    out_data: dict[str, Any] = {}
    for i, sub in enumerate(event_data):
        if sub != "??":
            try:
                key = subs[i].name
                val = subs[i].converter(sub)
                if val is not None:
                    out_data[key] = val
            except (TypeError, IndexError):
                continue
    return out_data
