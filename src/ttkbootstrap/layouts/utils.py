from __future__ import annotations
from typing import Tuple, Union

PadScalarOrPair = Union[int, Tuple[int, int]]

def add_pad(existing: PadScalarOrPair, extra: PadScalarOrPair) -> Tuple[int, int]:
    """Add scalar/pair padding values and return a (left/right or x, top/bottom or y) pair."""
    if isinstance(existing, tuple) and isinstance(extra, tuple):
        return existing[0] + extra[0], existing[1] + extra[1]
    if isinstance(existing, tuple):
        ex0 = extra if isinstance(extra, int) else extra[0]
        ex1 = extra if isinstance(extra, int) else extra[1]
        return existing[0] + ex0, existing[1] + ex1
    if isinstance(extra, tuple):
        return existing + extra[0], existing + extra[1]
    return existing + extra, existing + extra

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