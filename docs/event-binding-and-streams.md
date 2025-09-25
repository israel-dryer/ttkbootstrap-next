# Event binding & streams

Your widgets include a `BindingMixin` that centralizes event binding and emission, and layers a tiny FRP-style **Stream
** API on top of Tk’s event system.

## Why this exists

- **Safer bindings:** Per-event substitution strings are used so Tcl only expands fields an event actually needs; `%d`is
  braced as `{%d}` so JSON passed via `event_generate -data` isn’t split by Tcl.
- **Single source of truth:** All callbacks/`func_id`s are tracked for safe rebinding and cleanup.
- **Modern ergonomics:** A lazy `on(...)->Stream` lets you compose operators (`map`, `filter`, `tap`, `delay`,
  `debounce`, `throttle`, `idle`) and attach listeners with `listen()` / `then_stop()`.

## At a glance

```python
# Create a stream (no Tk binding yet):
stream = widget.on("<KeyRelease>")  # default scope="widget"

# Compose:
stream = stream.map(lambda e: e.char).filter(str.isalpha).debounce(200)

# Activate (this creates exactly one Tk binding behind the scenes):
sub = stream.listen(lambda ch: print("typed:", ch))

# Stop listening:
sub.unlisten()

# Programmatically raise a (virtual) event with JSON payload:
widget.emit("<<Change>>", data={"field": "email", "value": "alice@example.com"})
```

### Scopes

- `scope="widget"` (default) → `bind` on this widget
- `scope="all"` → `bind_all` (application-wide)
- `scope="TEntry"` (Tk class name) → `bind_class("TEntry", ...)`

A single dispatcher per `(scope, sequence)` fans out to all subscribers; if **any** listener returns `"break"`,
propagation stops (Tk receives `"break"`).

## How it compares to standard ttk/Tk

| Topic                 | Standard ttk/Tk                                         | This Library (`BindingMixin` + Streams)                                                  |
|-----------------------|---------------------------------------------------------|------------------------------------------------------------------------------------------|
| Binding API           | `widget.bind(seq, func, add)`, `bind_all`, `bind_class` | `on(event, scope=...) -> Stream`; terminal calls install the underlying Tk binding       |
| Event data expansion  | Global substitution script; easy to over-expand         | **Per-event** substitution via `event_substring(seq)` so only needed fields are expanded |
| JSON payloads         | N/A                                                     | `%d` is **braced** to `{%d}` so JSON stays intact                                        |
| Rebinding/cleanup     | Manual bookkeeping; easy to leak                        | Callbacks/func_ids tracked; `Subscription.unlisten()` detaches safely                    |
| Composition           | Manual function chains                                  | `map`, `filter`, `tap`, `delay`, `idle`, `debounce`, `throttle`                          |
| Stop propagation      | Return `"break"` from handler                           | Same—if **any** subscriber returns `"break"`, dispatcher returns `"break"`               |
| Emitting events       | `event_generate`                                        | `.emit(event, data=..., when="now)`                                                      |tail|head|mark")` with auto-JSON for virtual events |
| Global/class handlers | `bind_all`, `bind_class`                                | `on(event, scope="all")`                                                                 | "TEntry")` (same dispatcher rules) |

## Common patterns

### 1) Debounced text input (validation/search)

```python
entry.on("<KeyRelease>").map(lambda e: e.widget.get()).debounce(250).listen(lambda text: run_search(text))
```

### 2) Stop further handling after the first hit

```python
button.on("<Button-1>").then_stop()
```

### 3) Class-wide behavior for all `TEntry`

```python
self.on("<FocusIn>", scope="TEntry").tap(lambda e: e.widget.configure(style="Focus.TEntry")).listen(lambda _e: None)
```

### 4) Global escape key

```python
self.on("<Escape>", scope="all").listen(lambda _e: self.close_modal())
```

### 5) Emitting a virtual event with data

```python
# Somewhere deep in a widget:
self.emit("<<Change>>", field="count", value=42)

# Somewhere listening:
self.on("<<Change>>").listen(lambda e: handle_change(e.data))  # JSON intact
```

### 6) Throttle resize work

```python
root.on("<Configure>", scope="all").throttle(100, leading=False, trailing=True).listen(lambda e: relayout())
```

## Scheduling helpers

Streams created by `on(...)` are backed by a tiny scheduler that uses `after`/`after_idle`:

- `delay(ms)` — re-emit each value after `ms`
- `idle()` — re-emit at Tk idle (after current processing)
- `debounce(ms)` — emit after quiet period
- `throttle(ms, leading=True, trailing=True)` — cap emission rate

These operators automatically clean up timers when the last subscriber detaches.

## Emitting events

```python
widget.emit(event, data: dict | None = None, *, when = "now" | "tail" | "head" | "mark")
```

- For virtual events (`<<Name>>`) with `data`, payload is JSON-encoded and delivered intact thanks to braced
  substitutions.
- `when` mirrors Tk’s queue positions.

## Lifecycle & safety

- **Lazy bindings:** No Tk binding is installed until you call a **terminal** (`listen()`, `then_stop()`,
  `then_stop_when()`).
- **Fan-out dispatcher:** Exactly one underlying Tk binding per `(scope, sequence)`; it dispatches to all current
  subscribers.
- **Error isolation:** Exceptions in a subscriber don’t break the stream; consider routing to your error bus if desired.
- **Rebinding:** Internal tables enable safe rebinds (e.g., after theme/teardown scenarios).

## Quick migration from plain Tk

**Before (Tk):**

```python
def on_key(e):
    if not e.char.isalpha():
        return "break"


entry.bind("<KeyRelease>", on_key, add=True)
```

**After (this library):**

```python
entry.on("<KeyRelease>").map(lambda e: e.char).filter(str.isalpha).then_stop_when(
    lambda _ch: False)  # or .listen(...) and return "break" conditionally
```

Or more compact:

```python
entry.on("<KeyRelease>").listen(
    lambda e: "break" if not e.char.isalpha() else None
)
```

---

### API summary (for reference)

- `on(event, *, scope="widget"|"all"|TkClass) -> Stream`
- `Stream.map(f) -> Stream`
- `Stream.filter(pred) -> Stream`
- `Stream.tap(fn) -> Stream`
- `Stream.delay(ms) -> Stream`
- `Stream.idle() -> Stream`
- `Stream.debounce(ms) -> Stream`
- `Stream.throttle(ms, *, leading=True, trailing=True) -> Stream`
- `Stream.listen(fn) -> Subscription`
- `Stream.then_stop() -> Subscription`
- `Stream.then_stop_when(pred) -> Subscription`
- `Subscription.unlisten()` (aliases: `disconnect`, `dispose`)
- `emit(event, data=None, *, when="now"|"tail"|"head"|"mark")`
