"""
interop.foundation
------------------

Low-level building blocks for the interop layer.

This subpackage contains utilities that have **no dependencies on other
interop modules** and can be safely imported anywhere. It forms the base
layer for higher-level specs (`interop.spec`) and runtime helpers
(`interop.runtime`).

Contents:
- `events` — integer constants for Tk/X11 events (`EventEnum`).
- `keyresolve` — helpers for decoding modifier states and resolving keypress
  descriptors.
- `prune` — functions and mixins for pruning dataclass/namespace payloads
  (`prune_payload`, `prune_namespace`, `PrunableEventMixin`).

Importing from this layer should never cause circular dependencies. Higher
layers (spec/runtime) may depend on `foundation`, but not the other way
around.
"""
