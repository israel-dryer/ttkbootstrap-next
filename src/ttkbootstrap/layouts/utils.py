from __future__ import annotations

from typing import Any, Optional, Tuple, Union

type Pad = Union[int, Tuple[int, int]]
PadScalarOrPair = Union[int, Tuple[int, int]]


def _to_pair(v: Optional[Pad]) -> Tuple[int, int]:
    if v is None:
        return 0, 0
    if isinstance(v, tuple):
        if len(v) == 2:
            return int(v[0]), int(v[1])
        # Unexpected shapes collapse to 0,0 defensively
        return (0, 0)
    return int(v), int(v)


def add_pad(existing: Optional[PadScalarOrPair], extra: Optional[PadScalarOrPair]) -> Tuple[int, int]:
    """Add scalar/pair padding values; always return a (x, y) pair."""
    ex_x, ex_y = _to_pair(existing)
    ad_x, ad_y = _to_pair(extra)
    return ex_x + ad_x, ex_y + ad_y


def margin_to_pad(margin) -> Tuple[PadScalarOrPair, PadScalarOrPair]:
    """Return (padx, pady) to be added to gap padding."""
    if isinstance(margin, int):
        return margin, margin
    if isinstance(margin, tuple) and len(margin) == 2:  # (x, y)
        x, y = margin
        return x, y
    if isinstance(margin, tuple) and len(margin) == 4:  # (t, r, b, l)
        t, r, b, l = margin
        return (l, r), (t, b)
    return 0, 0


def normalize_gap(gap: Union[int, Tuple[int, int]]) -> Tuple[int, int]:
    return (gap, gap) if isinstance(gap, int) else gap


def normalize_padding(pad: Union[int, Tuple[int, int], Tuple[int, int, int, int]] | None) -> Tuple[int, int, int, int]:
    if pad is None:
        return 0, 0, 0, 0
    if isinstance(pad, int):
        return pad, pad, pad, pad
    if len(pad) == 2:
        # (x, y) -> (top, right, bottom, left)
        return pad[1], pad[0], pad[1], pad[0]
    return pad


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
            raise Exception("Must be a an integer, float or value in the format of '25px' or '50%'")
    else:
        raise Exception("Must be a an integer, float or value in the format of '25px' or '50%'")
