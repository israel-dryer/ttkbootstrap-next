from __future__ import annotations
from typing import Iterable, Mapping, Optional, Type, Union, Any

from ttkbootstrap.types import IconPosition
from ttkbootstrap.exceptions import LayoutError, UIError


def clamp(value, min_val, max_val):
    """Return a value that is bounded by a minimum and maximum.

    Args:
        value: The value to evaluate.
        min_val: The minimum allowed value.
        max_val: The maximum allowed value.

    Returns:
        The value, constrained between `min_val` and `max_val`.
    """
    return min(max(value, min_val), max_val)


def unsnake(string):
    """Remove underscores from a snake_case string.

    Args:
        string (str): A string containing underscores.

    Returns:
        str: The string with underscores removed.
    """
    return string.replace('_', '')


def unsnake_kwargs(kwargs):
    """Remove underscores from snake_case key"""
    return {unsnake(k): v for k, v in kwargs.items()}


def resolve_options(obj: Union[dict, str], default_key: str):
    """Coerce to an object of options"""
    if obj is None:
        return dict()
    if isinstance(obj, str):
        return {default_key: obj}
    return obj


def parse_dim(value: Any):
    if isinstance(value, int):
        return value, False
    if isinstance(value, float):
        return value, value <= 1.0
    if isinstance(value, str):
        if value.endswith('%'):
            return float(value.replace('%', '')) / 100, True
        elif value.endswith('px'):
            return float(value.replace('px', '')), False
        else:
            return value, False
    else:
        raise Exception("Must be a an integer, float or value in the format of '25px' or '50%'")


def clean_layout_keys(kwargs):
    """Return a dictionary of regular kwargs and layout kwargs"""
    layout_keys = {
        "rows", "columns", "gap", "direction", "padding",
        "row", "column", "rowspan", "colspan"
    }
    tk_kwargs = {k: v for k, v in kwargs.items() if k not in layout_keys}
    layout_kwargs = {k: v for k, v in kwargs.items() if k in layout_keys}
    return tk_kwargs, layout_kwargs


def resolve_parent(parent: Any):
    if parent is None:
        return parent
    elif getattr(parent, 'widget', None) is None:
        return parent
    else:
        return parent.widget


def allowed_keys_for_typed_dict(typed_dict_cls: type) -> frozenset[str]:
    """
    Return all allowed keys for a TypedDict class (Python 3.13+).
    """
    # PEP 655 guarantees these exist at runtime in 3.13+
    req = getattr(typed_dict_cls, "__required_keys__", set())
    opt = getattr(typed_dict_cls, "__optional_keys__", set())
    # Fall back to annotations if needed (defensive)
    if not req and not opt:
        ann = getattr(typed_dict_cls, "__annotations__", {})
        return frozenset(ann.keys())
    return frozenset(req | opt)


def invalid_keys_for_typed_dict(
        options: Mapping[str, Any],
        typed_dict_cls: type,
        *,
        extra_allowed: Iterable[str] = (),
        forbidden: Iterable[str] = (),
) -> list[str] | None:
    """
    Return a sorted list of invalid keys in `options` for the given TypedDict, or None if valid.

    - `extra_allowed`: keys to allow in addition to the TypedDict (e.g., aliases/compat).
    - `forbidden`: keys to explicitly disallow even if present in the TypedDict
                   (useful for cross-layout guards, e.g., blocking grid keys in pack).
    """
    allowed = set(allowed_keys_for_typed_dict(typed_dict_cls))
    allowed.update(extra_allowed)

    keys = set(options.keys())
    bad_unknown = keys - allowed
    bad_forbidden = keys & set(forbidden)

    invalid = sorted(bad_unknown | bad_forbidden)
    return invalid or None


def assert_valid_keys(
        options: Mapping[str, Any],
        typed_dict_cls: type,
        *,
        where: str,
        forbidden: Iterable[str] = (),
        extra_allowed: Iterable[str] = (),
        exc_cls: Type[UIError] = LayoutError,
        code: str | None = None,
        hint: str | None = None,
) -> None:
    """
    Raise `exc_cls` if `options` includes keys not allowed
    by `typed_dict_cls` (and not in `extra_allowed`) or keys explicitly `forbidden`.

    Parameters
    ----------
    options:
        The runtime kwargs to validate.
    typed_dict_cls:
        The TypedDict class defining allowed keys.
    where:
        A label used in the error message (e.g. "pack", "grid", "place").
    forbidden:
        Keys explicitly disallowed for this context.
    extra_allowed:
        Extra keys permitted in addition to the TypedDict.
    exc_cls:
        Exception subclass of UIError to raise (default=LayoutError).
    code:
        Optional error code string.
    hint:
        Optional override for the error hint (default will list allowed keys).
    """
    invalid = invalid_keys_for_typed_dict(
        options, typed_dict_cls, extra_allowed=extra_allowed, forbidden=forbidden
    )
    if invalid:
        allowed = ", ".join(sorted(allowed_keys_for_typed_dict(typed_dict_cls) | set(extra_allowed)))
        bad = ", ".join(sorted(invalid))
        raise exc_cls(
            f"Invalid keyword option(s) for {where}: {bad}.",
            hint=hint or f"Allowed: {allowed}.",
            code=code or f"{where.upper()}_INVALID_KEYS",
        ) from None


def _is_rtl() -> bool:
    # If you have app-level locale/dir, check it here. Stubbed as False for now.
    return False


def normalize_icon_position(icon_position: IconPosition, *, has_text: bool, has_icon: bool) -> Optional[str]:
    """
    Convert `icon_position` to Tkinter's `compound` value, with smart defaults.

    - auto + only icon    -> center
    - auto + icon + text  -> start (LTR) / end (RTL)
    - auto + only text    -> None
    """
    _ICON_POSITION_MAP = {
        "start": "left",
        "end": "right",
        "top": "top",
        "bottom": "bottom",
        "center": "center",
        None: None,
    }

    if icon_position not in (None, "auto", "start", "end", "top", "bottom", "center"):
        raise ValueError("icon_position must be one of None|'auto'|'start'|'end'|'top'|'bottom'|'center'.")

    if icon_position == "auto":
        if has_icon and not has_text:
            return "image"
        if has_icon and has_text:
            return "right" if _is_rtl() else "left"  # end for RTL, start for LTR
        return None

    return _ICON_POSITION_MAP[icon_position]
