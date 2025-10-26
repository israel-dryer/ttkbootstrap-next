"""
interop.runtime.event_factory
-----------------------------

Runtime factory for constructing minimal, per-event payload objects (slots
dataclasses) from raw Tcl substitution values.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Callable, Dict, List, Sequence, Tuple, Type

from ttkbootstrap_next.interop.runtime.event_types import (
    BaseEvent,
    ButtonEvent,
    ConfigureEvent,
    KeyEvent,
    MotionEvent,
    UnknownEvent,
    WheelEvent,
    WidgetEvent,
)
from ttkbootstrap_next.interop.spec.profiles import fields_for, pattern_for
from ttkbootstrap_next.interop.spec.subs import Sub, event_subs

# Build a fast lookup: field name -> Sub (to access its converter)
_SUB_BY_NAME: Dict[str, Sub] = {s.name: s for s in event_subs}

# Map a pattern to the corresponding event dataclass
_CLASS_BY_PATTERN: Dict[str, Type[BaseEvent]] = {
    "key": KeyEvent,
    "button": ButtonEvent,
    "motion": MotionEvent,
    "wheel": WheelEvent,
    "configure": ConfigureEvent,
    "widget": WidgetEvent,
    "virtual": WidgetEvent,  # virtuals use the simple WidgetEvent shape
}


@lru_cache(maxsize=256)
def event_class_for(event_name: str) -> Type[BaseEvent]:
    """Return the dataclass type to instantiate for the given event."""
    return _CLASS_BY_PATTERN.get(pattern_for(event_name), UnknownEvent)


@lru_cache(maxsize=256)
def _converters_for(event_name: str) -> Tuple[List[str], Tuple[Callable[[str], object], ...]]:
    """
    Internal: resolve the ordered field names and their converter callables
    for a specific event, with results cached.
    """
    names = fields_for(event_name)
    convs = tuple(_SUB_BY_NAME[n].converter for n in names)
    return names, convs


@lru_cache(maxsize=256)
def builder_for(event_name: str) -> Callable[[str, Sequence[str]], BaseEvent]:
    """
    Return a fast builder closure for `event_name` that converts raw args
    and instantiates the appropriate event class.
    """
    names, convs = _converters_for(event_name)
    cls = event_class_for(event_name)

    def _convert(v: str, conv: Callable[[str], object]):
        # Treat Tcl's unknown/sentinel '??' as None, else apply converter.
        if v == "??":
            return None
        try:
            return conv(v)
        except Exception:
            # Defensive: if a converter fails, surface None (avoid hot-path crashes).
            return None

    def build(name: str, raw: Sequence[str]) -> BaseEvent:
        # Convert in positional order (zip is safe for slight arity mismatches).
        vals = [_convert(v, conv) for conv, v in zip(convs, raw)]
        mapped = dict(zip(names, vals))

        # Ensure `data` is always a dict (transforms rely on it)
        data_val = mapped.pop("data", None)
        if not isinstance(data_val, dict):
            data_val = {}

        # Instantiate minimal, specific event class
        return cls(name=name, data=data_val, **mapped)  # type: ignore[arg-type]

    return build


def build_event(event_name: str, raw: Sequence[str]) -> BaseEvent:
    """Build and return a minimal event payload for the given event name."""
    return builder_for(event_name)(event_name, raw)
