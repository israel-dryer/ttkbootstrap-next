"""
interop.foundation.prune
-----------------------

Pruning utilities for event/dataclass payloads with two complementary modes:

1) JSON mode (`prune_payload`) – converts dataclasses to plain dicts and
   removes empty/zero-ish values recursively. Ideal for serialization.
2) Namespace mode (`prune_namespace`) – converts dataclasses to a
   `NamedNamespace` where empty fields are omitted and the repr shows the
   originating dataclass name (e.g., `EventInput(...)`). Great for logs
   and debugging while keeping an object-like feel.

Also included:
- `NamedNamespace`: a SimpleNamespace with a friendly, per-instance type label.
- `namespace_to_dict`: converts a (possibly nested) NamedNamespace tree to dicts.
- `PrunableEventMixin`: adds `to_payload()` (namespace) and `to_payload_dict()`
  (dict) to your dataclasses.

Typical usage:

    @dataclass
    class EventInput(PrunableEventMixin):
        keysym: str | None = None
        state: int | None = None

    ei = EventInput(keysym="a", state=0)
    ns = ei.to_payload(drop_zeros=True)        # -> EventInput(keysym='a')
    d  = ei.to_payload_dict(drop_zeros=True)   # -> {'keysym': 'a'}
"""

from __future__ import annotations
from dataclasses import is_dataclass, fields, dataclass
from types import SimpleNamespace
from typing import Any, Mapping, Sequence

__all__ = [
    "NamedNamespace",
    "prune_payload", "prune_namespace", "namespace_to_dict",
    "prune", "PrunableEventMixin",
]

_EMPTY = (None, "", (), [], {})  # tweak as needed


# ---------------------------
# Small helper / pretty repr
# ---------------------------
class NamedNamespace(SimpleNamespace):
    """SimpleNamespace whose repr shows a friendly type label."""
    __typename__: str = "Namespace"

    def __repr__(self) -> str:
        body = ", ".join(f"{k}={v!r}" for k, v in vars(self).items() if k != "__typename__")
        return f"{self.__typename__}({body})"


def _is_empty(v: Any, drop_zeros: bool) -> bool:
    """Return True if value is considered empty (and optionally zero)."""
    if v in _EMPTY:
        return True
    if drop_zeros and v == 0:
        return True
    return False


# ------------------------------------
# Mode 1: JSON-ready (dict) pruning
# ------------------------------------
def prune_payload(
        obj: Any,
        *,
        drop_zeros: bool = False,
        drop_empty_dataclasses: bool = True,
) -> Any:
    """Recursively prune empties; dataclasses become dicts."""
    if is_dataclass(obj):
        d: dict[str, Any] = {}
        for f in fields(obj):
            val = prune_payload(
                getattr(obj, f.name),
                drop_zeros=drop_zeros,
                drop_empty_dataclasses=drop_empty_dataclasses,
            )
            if _is_empty(val, drop_zeros):
                continue
            d[f.name] = val
        return None if (drop_empty_dataclasses and not d) else d

    if isinstance(obj, Mapping):
        out = {
            k: prune_payload(v, drop_zeros=drop_zeros, drop_empty_dataclasses=drop_empty_dataclasses)
            for k, v in obj.items()
        }
        return {k: v for k, v in out.items() if not _is_empty(v, drop_zeros)}

    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        lst = [
            prune_payload(v, drop_zeros=drop_zeros, drop_empty_dataclasses=drop_empty_dataclasses)
            for v in obj
        ]
        return [v for v in lst if not _is_empty(v, drop_zeros)]

    return obj


# ------------------------------------------------------
# Mode 2: Namespace-style pruning with custom type names
# ------------------------------------------------------
def _to_named_namespace_value(
        value: Any,
        *,
        drop_zeros: bool,
        drop_empty_dataclasses: bool,
        typename: str | None,  # suggested label for this level; fallback to class name
) -> Any:
    """Internal: convert/prune to NamedNamespace (or plain containers)."""
    # Dataclass → NamedNamespace (with class name label)
    if is_dataclass(value):
        data: dict[str, Any] = {}
        for f in fields(value):
            pv = _to_named_namespace_value(
                getattr(value, f.name),
                drop_zeros=drop_zeros,
                drop_empty_dataclasses=drop_empty_dataclasses,
                typename=None,  # nested: derive from nested class
            )
            if _is_empty(pv, drop_zeros):
                continue
            data[f.name] = pv

        if not data and drop_empty_dataclasses:
            return None

        ns = NamedNamespace(**data)
        ns.__typename__ = typename or type(value).__name__
        return ns

    # Mapping → dict (values recursively converted)
    if isinstance(value, Mapping):
        out = {
            k: _to_named_namespace_value(
                v,
                drop_zeros=drop_zeros,
                drop_empty_dataclasses=drop_empty_dataclasses,
                typename=None,
            )
            for k, v in value.items()
        }
        return {k: v for k, v in out.items() if not _is_empty(v, drop_zeros)}

    # Sequence (not str/bytes) → list contents recursively converted
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        items = [
            _to_named_namespace_value(
                v,
                drop_zeros=drop_zeros,
                drop_empty_dataclasses=drop_empty_dataclasses,
                typename=None,
            )
            for v in value
        ]
        return [v for v in items if not _is_empty(v, drop_zeros)]

    # Primitive / everything else unchanged
    return value


def prune_namespace(
        obj: Any,
        *,
        drop_zeros: bool = False,
        drop_empty_dataclasses: bool = True,
        typename: str | None = None,
) -> NamedNamespace | None | list | dict | Any:
    """Recursively prune empties; dataclasses become NamedNamespace."""
    return _to_named_namespace_value(
        obj,
        drop_zeros=drop_zeros,
        drop_empty_dataclasses=drop_empty_dataclasses,
        typename=typename or (type(obj).__name__ if is_dataclass(obj) else None),
    )


# -------------------------------
# Utility: turn NS payload into dict
# -------------------------------
def namespace_to_dict(value: Any) -> Any:
    """Convert a NamedNamespace tree to plain dict/list structures."""
    if isinstance(value, NamedNamespace):
        return {k: namespace_to_dict(v) for k, v in vars(value).items() if k != "__typename__"}
    if isinstance(value, Mapping):
        return {k: namespace_to_dict(v) for k, v in value.items()}
    if isinstance(value, list):
        return [namespace_to_dict(v) for v in value]
    if isinstance(value, tuple):
        return [namespace_to_dict(v) for v in value]
    return value


# -----------------------
# Mixin: use NamedNamespace
# -----------------------
@dataclass
class PrunableEventMixin:
    """Add `to_payload()` (namespace) and `to_payload_dict()` (dict) to dataclasses."""

    def to_payload(
            self,
            *,
            drop_zeros: bool = False,
            drop_empty_dataclasses: bool = True,
            typename: str | None = None,
    ) -> NamedNamespace | None:
        """Return a pruned NamedNamespace; repr label defaults to class name."""
        return prune_namespace(
            self,
            drop_zeros=drop_zeros,
            drop_empty_dataclasses=drop_empty_dataclasses,
            typename=typename or type(self).__name__,
        )

    def to_payload_dict(
            self,
            *,
            drop_zeros: bool = False,
            drop_empty_dataclasses: bool = True,
    ) -> dict:
        """Return a pruned plain dict suitable for JSON."""
        ns = self.to_payload(drop_zeros=drop_zeros, drop_empty_dataclasses=drop_empty_dataclasses)
        return {} if ns is None else namespace_to_dict(ns)

    def __repr__(self) -> str:
        """Pretty repr using the pruned NamedNamespace view."""
        return f"{type(self).__name__}({self.to_payload()})"

