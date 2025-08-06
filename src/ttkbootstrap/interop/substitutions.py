from typing import Callable

from ttkbootstrap.interop.constants import event_subs
from ttkbootstrap.interop.types import Sub
from ttkbootstrap.interop.utils import get_substring


def register_event_sub(name: str, code: str, converter: Callable):
    """Allow runtime extension of event substitutions."""
    event_subs.append(Sub(name, code, converter))


def get_event_substring() -> str:
    global _event_sub_string
    if _event_sub_string is None:
        _event_sub_string = get_substring(event_subs)
    return _event_sub_string


_event_sub_string = None
