"""
interop.spec
------------

Static specifications for event interop.

This subpackage defines the *schema layer* of the interop system. It
contains the constants, converters, and type definitions that describe
how raw Tcl/Tk event substrings are mapped into structured Python
payloads.

Modules
-------
- **types** — core dataclasses for structured event payloads
  (`UIEvent`, `EventInput`, `EventGeometry`, etc.), plus `Sub` and
  `Trace` descriptors.
- **constants** — predefined lists of `Sub` entries (`event_subs`,
  `validation_subs`) that specify Tcl substitution codes and their
  converters.
- **converters** — functions for transforming raw Tcl string values
  (timestamps, state bits, JSON blobs, event codes) into Python types.

Design
------
- The spec layer is *purely declarative* and has no runtime side effects.
- It may depend on `interop.foundation` utilities (e.g., `EventEnum`,
  pruning), but never on `interop.runtime`.
- At runtime, the helpers in `interop.runtime` consume these specs to
  construct structured `UIEvent` payloads.

Typical usage
-------------
Applications usually do not import directly from `interop.spec`.
Instead, runtime utilities (`interop.runtime.utils`,
`interop.runtime.commands`) rely on these specs when converting raw
event data into typed objects.
"""
