"""
interop
-------

Cross-cutting interop layer for `ttkbootstrap`.

This package provides the glue between raw Tcl/Tk event data and the
high-level event system used throughout `ttkbootstrap`. It is organized
into three layers:

- **foundation**
  Low-level, dependency-free utilities. Includes:
    - `events` (numeric event codes, `EventEnum`)
    - `keyresolve` (decode modifier states, resolve canonical presses)
    - `prune` (payload pruning and `PrunableEventMixin`)

- **spec**
  Declarative schema for event payloads. Includes:
    - `types` (dataclasses like `UIEvent`, `EventInput`, `EventGeometry`)
    - `constants` (lists of `Sub` substitutions: `event_subs`,
      `validation_subs`)
    - `converters` (functions to map raw Tcl values to Python types)

- **runtime**
  Execution-time helpers that consume `spec` and `foundation`. Includes:
    - `utils` (map raw substrings to structured payloads)
    - `commands` (register Python callables as Tcl commands, with error
      handling)
    - `substitutions` (manage/extend the substitution string for Tcl)

Design
------
- `foundation` may be imported by both `spec` and `runtime`.
- `spec` may depend on `foundation` but not `runtime`.
- `runtime` may depend on both `spec` and `foundation`.

This layered approach prevents circular imports and keeps responsibilities
clear: **foundation = primitives, spec = schema, runtime = behavior**.
"""
