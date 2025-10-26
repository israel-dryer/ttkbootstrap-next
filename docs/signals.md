# Signals

A **Signal** is a typed, reactive wrapper around a Tk variable (e.g., `StringVar`, `IntVar`). It gives you:

- **Simple value access**: call the signal to read its current value.
- **Type safety**: `.set(value)` enforces the original Python type.
- **Subscriptions**: `.subscribe(fn)` to be notified whenever the value changes.
- **Derivations**: `.map(transform)` to create a *derived* signal that stays in sync.
- **Direct Tk interop**: pass `signal.name` (or `str(signal)`) anywhere Tk/ttk expects a `textvariable`/`variable`.

Under the hood, Signals are backed by a native `tk.Variable` and use `trace_add("write", ...)` to react to
updates—whether they come from your code or from the user typing into a widget. A small helper manages adding/removing
those traces.

---

## Core API (at a glance)

```python
from ttkbootstrap_next.signals import Signal

name = Signal("Alice")  # type: str → StringVar under the hood
age = Signal(42)  # type: int  → IntVar
ok = Signal(True)  # type: bool → BooleanVar

print(name())  # read current value (callable)
name.set("Bob")  # typed setter (TypeError on mismatch)

fid = name.subscribe(lambda v: print("name changed to", v))
name.unsubscribe_all()  # or .unsubscribe(callback)

upper_name = name.map(str.upper)  # derived Signal[str] that stays synced
```

How it connects to Tk widgets:

```python
entry = ttk.Entry(root, textvariable=name.name)  # or textvariable=str(name)
spin = ttk.Spinbox(root, textvariable=age.name)
check = ttk.Checkbutton(root, variable=ok.name)
```

Because a Signal *is* a Tk variable under the hood, **edits in the widget update the Signal**, and `.subscribe(...)`
callbacks fire automatically.

---

## What makes Signals different from Tk/ttk variables?

| Topic                | Plain Tk/ttk variable (`StringVar`, `IntVar`, …)   | Signal                                                                              |
|----------------------|----------------------------------------------------|-------------------------------------------------------------------------------------|
| Value access         | `var.get()` / `var.set(x)`                         | `sig()` to read, `sig.set(x)` to write (typed)                                      |
| Type safety          | You *can* set mismatched types (sometimes coerced) | Enforces the original Python type; raises `TypeError` on mismatch                   |
| Reactivity           | Manual `trace_add('write', cb)` and bookkeeping    | `.subscribe(cb)` returns a trace id; `.unsubscribe` / `.unsubscribe_all()` provided |
| Transformations      | You do it yourself and keep two vars in sync       | `.map(f)` returns a **derived Signal** that auto-updates when the source changes    |
| Interop with widgets | Pass `var` directly                                | Pass `signal.name` or `str(signal)`—it’s the Tcl variable name                      |
| Error handling       | `get()` may raise `TclError` if unset/destroyed    | `sig()` can provide typed defaults and centralize error handling                    |
| Introspection        | You track trace ids and callbacks manually         | The signal stores trace ids and manages remove/cleanup for you                      |

All of the above behavior comes from wrapping a real `tk.Variable`, attaching traces, and maintaining a map of
subscribers (callback → id). Derived signals are created by seeding with `transform(source())` and keeping it updated
whenever the source changes.

---

## Practical patterns

### 1) Bind a widget to a signal and react to changes

```python
email = Signal("")

ttk.Entry(root, textvariable=email.name)


def on_email(v: str):
    print("validate:", v)


email.subscribe(on_email)
```

Any keystroke that mutates the entry updates the Signal and triggers `on_email`.

### 2) Derived (computed) form fields

```python
first = Signal("Ada")
last = Signal("Lovelace")

full = first.map(lambda f: f.strip())
    .map(lambda f: f + " " + last().strip())

# full is a live Signal[str]; if first changes, full updates.
ttk.Label(root, textvariable=full.name)
```

Because `.map` returns another Signal, you can chain transforms and still treat the result like any other Tk variable.

### 3) Enforcing types

```python
count = Signal(0)
count.set(1)  # ok
count.set("1")  # raises TypeError
```

The constructor selects the correct Tk var (`IntVar`, `DoubleVar`, `BooleanVar`, or `StringVar`) from the **initial
value’s type**—and `.set` enforces that same type later.

### 4) Clean shutdown

```python
sid = some_signal.subscribe(handler)
some_signal.unsubscribe(handler)  # or:
some_signal.unsubscribe_all()
```

No stray traces left behind—the signal removes its `trace_add` handlers for you.

---

## Mental model

- A **Signal** is a *typed* Tk variable + ergonomic **reactivity**.
- **Subscribe** to it instead of wiring raw `trace_add` calls.
- Build **derived signals** with `.map()` instead of hand-syncing multiple Tk variables.
- Pass `signal.name` anywhere Tk expects a variable; everything stays in lock-step.
