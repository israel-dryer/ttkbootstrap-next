"""
interop.runtime
---------------

Runtime layer for event interop.

This subpackage provides the **execution-time utilities** that sit on top
of the lower-level specs (`interop.spec`) and foundation primitives
(`interop.foundation`). Whereas `spec` defines static data structures and
constants, `runtime` contains the glue that interacts with Tcl/Tk at
runtime.

Modules
-------
- **utils** — helpers for mapping raw Tcl event substrings into structured
  `UIEvent` payloads and sub-payloads.
- **commands** — wrappers that register Python callables as Tcl commands
  (generic, trace, and event callbacks), with pluggable error handling.
- **substitutions** — helpers for managing and extending the event
  substitution string passed to Tcl when binding events.

Design
------
- Runtime modules may import from `interop.spec` and `interop.foundation`
  but should not be imported by them.
- All structured payloads produced here use the pruning utilities from
  `interop.foundation.prune` (via `PrunableEventMixin`).

Typical usage
-------------
Applications rarely import from `interop.runtime` directly. Instead,
these utilities are used internally by higher-level event binding and
widget APIs in `ttkbootstrap`. They ensure that raw event data from Tcl
is converted into Python-friendly, typed objects before being delivered
to user callbacks.
"""
