# Validation system

A lightweight, event-driven layer that lets widgets declare **rules**, run them automatically on **user interaction**,
and publish **virtual events** (`<<Invalid>>`, `<<Valid>>`, `<<Validated>>`) with structured payloads. Results are
carried by
a small data object: `ValidationResult(is_valid: bool, message: str)`.

## Building blocks

- **ValidationResult** — normalized outcome of a single rule; includes a human message for UI feedback.
- **ValidationRule** — encapsulates rule type (`required`, `email`, `stringLength`, `pattern`, `custom`, …),
  default/override **message**, per-rule **trigger**, and any params (`min`, `max`, `pattern`, `func`).
  `validate(value)` returns a `ValidationResult`. Defaults include sensible messages and triggers per rule type.
- **Rule types & triggers** — strongly typed literals and a `ValidationOptions` typed dict (`pattern`, `message`, `min`,
  `max`, `trigger`, `func`) keep the API explicit. Triggers: `'key'`, `'blur'`, `'always'`, `'manual'`.
- **ValidationMixin** — attach to input widgets. Provides:
    - `add_validation_rule(type, **options)` and `add_validation_rules([...])`
    - Automatic binding: **keyup** and **blur** are debounced and routed to `validate(value, trigger)`
    - Emits `<<Invalid>>`, `<<Valid>>`, and `<<Validated>>` with `{value, is_valid, message}`
    - Convenience stream helpers: `.on_valid(...)`, `.on_invalid(...)`, `.on_validated(...)`

## Event flow

1) User types → the mixin’s debounced **KEYUP** stream calls `validate(value, "key")`. Losing focus calls
   `validate(value, "blur")`.
2) Each rule decides whether to run based on its **trigger** (e.g., `email` might run on `'always'`, `required` on
   `'blur'`).
3) First failing rule emits `<<Invalid>>` (with `message`) and then `<<Validated>>`, returning `False`. If all
   applicable rules pass, emits `<<Valid>>` and `<<Validated>>`.

## Usage

### Declarative rules on a widget

```python
entry.add_validation_rule("required", message="Email is required")
entry.add_validation_rule("email")  # default message

# React to results (streams or direct binding)
entry.on_invalid(lambda e: show_error(e.data["message"]))
entry.on_valid(lambda e: clear_error())
```

`required` typically runs on blur; `email` runs “always” (key+blur), per defaults.

### Custom rule and manual trigger

```python
def not_example(v: str) -> bool:
    return "example.com" not in (v or "")


entry.add_validation_rule(
    "custom", func=not_example,
    message="example.com emails not allowed",
    trigger="manual")

# Somewhere else:
entry.validate(entry.value(), trigger="manual")
```

Custom rules supply a Python predicate and can opt into `'manual'` only.

---

# How this differs from standard Tk

| Area                   | Plain Tk/Tkinter                                           | This library                                                                                                        |
|------------------------|------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Where validation lives | Scattered: widget callbacks, variable traces, ad-hoc flags | Centralized per-widget **rule list** + typed options; uniform `ValidationResult` for outcomes                       |
| When validation runs   | You wire events manually and remember to throttle/debounce | **Built-in triggers** (`key`, `blur`, `always`, `manual`) with sensible defaults; key/blur are **debounced**        |
| Rule declaration       | Custom functions sprinkled across handlers                 | **Declarative**: `add_validation_rule(type, **options)` with typed params (`pattern`, `min/max`, `func`, `message`) |
| Feedback channel       | You call `configure()` / labels / messageboxes yourself    | Emits **virtual events**: `<<Invalid>>`, `<<Valid>>`, `<<Validated>>` carrying `{value, is_valid, message}`         |
| Composability          | Manual if/else chains                                      | Rules run **in order**; first failure short-circuits; success emits consistent signals                              |
| Reuse & testability    | Logic tied to UI callbacks                                 | Rules are small, testable units (`ValidationRule.validate`) returning a pure `ValidationResult`                     |

## Mental model

- **Rules** are small validators with a **when** (trigger) and a **what** (check).
- The widget **mixes in** validation: it listens to user events, chooses which rules to run, and **emits events** you
  can subscribe to—keeping UI feedback decoupled and declarative.
