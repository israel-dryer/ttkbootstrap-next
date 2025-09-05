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

from ttkbootstrap.interop.spec.constants import event_subs
from ttkbootstrap.interop.spec.types import (
    EventGeometry, EventInput, EventMeta, EventRef,
    EventValidation, EventWindowing, Sub, UIEvent,
)
from ttkbootstrap.interop.foundation.keyresolve import decode_mods, resolve_press_from_parts

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


def _post_process(event_dict: dict[str, Any]) -> dict[str, Any]:
    """Attach derived fields and wrap substructures."""
    state = event_dict.get("state")
    keysym = event_dict.get("keysym") or event_dict.get("key")
    char = event_dict.get("char")

    mods = decode_mods(state, keysym=keysym, include_caps=False)
    if mods is not None:
        event_dict["mods"] = tuple(mods)

    press = resolve_press_from_parts(state=state, keysym=keysym, char=char, include_caps=False)
    if press is not None:
        event_dict["press"] = press.as_string()

    return {
        "name": event_dict.get("name"),
        "timestamp": event_dict.get("timestamp"),
        "data": event_dict.get("data", {}),
        "input": get_input_subs(event_dict),
        "geometry": get_geometry_subs(event_dict),
        "windowing": get_windowing_subs(event_dict),
        "ref": get_ref_subs(event_dict),
        "meta": get_meta_subs(event_dict),
        "validation": get_validation_subs(event_dict),
    }


def get_event_namedtuple(event_name: str, raw_data: Sequence[str]) -> Any:
    """Build a pruned UIEvent payload from raw event data."""
    event_dict = {"name": event_name}
    event_dict.update(map_event_data(raw_data, event_subs))
    out_data = _post_process(event_dict)
    return UIEvent(**out_data).to_payload()


# --- Sub-payload builders --------------------------------------------------

def get_input_subs(event_dict: dict[str, Any]):
    """Wrap input-related fields in EventInput."""
    ev = EventInput(
        press=event_dict.get("press"),
        mods=event_dict.get("mods"),
        keysym=event_dict.get("keysym"),
        char=event_dict.get("char"),
        state=event_dict.get("state"),
        delta=event_dict.get("delta"),
    )
    return ev.to_payload()


def get_geometry_subs(event_dict: dict[str, Any]):
    """Wrap geometry fields in EventGeometry."""
    ev = EventGeometry(
        width=event_dict.get("width"),
        height=event_dict.get("height"),
        x=event_dict.get("x"),
        y=event_dict.get("y"),
        x_root=event_dict.get("x_root"),
        y_root=event_dict.get("y_root"),
        border_width=event_dict.get("border_width"),
    )
    return ev.to_payload()


def get_windowing_subs(event_dict: dict[str, Any]):
    """Wrap windowing fields in EventWindowing."""
    ev = EventWindowing(
        window=event_dict.get("window"),
        subwindow=event_dict.get("subwindow"),
        send_event=event_dict.get("send_event"),
        override_redirect=event_dict.get("override_redirect"),
        focus=event_dict.get("focus"),
    )
    return ev.to_payload()


def get_ref_subs(event_dict: dict[str, Any]):
    """Wrap widget reference fields in EventRef."""
    ev = EventRef(
        root=event_dict.get("root"),
        widget=event_dict.get("widget"),
    )
    return ev.to_payload()


def get_meta_subs(event_dict: dict[str, Any]):
    """Wrap metadata fields in EventMeta."""
    ev = EventMeta(
        mode=event_dict.get("mode"),
        place=event_dict.get("place"),
        property=event_dict.get("property"),
    )
    return ev.to_payload()


def get_validation_subs(event_dict: dict[str, Any]):
    """Wrap validation fields in EventValidation."""
    ev = EventValidation(
        action_type=event_dict.get("action_type"),
        char_index=event_dict.get("char_index"),
        validation_value=event_dict.get("validation_value"),
        current_value=event_dict.get("current_value"),
        insert_value=event_dict.get("insert_value"),
        condition=event_dict.get("condition"),
    )
    return ev.to_payload()
