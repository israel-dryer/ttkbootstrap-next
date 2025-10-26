# Minimum Compatibility Plan for ttkbootstrap_next v2

This plan outlines a **small, sustainable** compatibility layer that preserves the clean v2 architecture while
minimizing migration pain for v1/Tk users. It focuses on two universal bridges and two widget-specific adapters.

---

## Core idea

Add **two tiny adapters** (plus two widget-specific shims) that cover 90% of migrations:

1. **`command=` sugar** → internally wire to the v2 event stream.
2. **`*variable=` / `textvariable=` interop** → accept either Tk vars **or** v2 `Signal`.
3. **`Text` adapter** → optional `textvariable`/`Signal` sync + `<<Modified>>` bridging.
4. **`Canvas` adapter** → optional sugar for item events; keep native API intact.

Everything else stays pure v2 (streams, builders, containers, icons, validation).

---

## 0) Tiny utilities (one-time)

```python

# signals_compat.py

from tkinter import StringVar, IntVar, DoubleVar, BooleanVar

_TK_VARS = (StringVar, IntVar, DoubleVar, BooleanVar)


def to_signal(value_or_var, *, default=None, factory):


    """
    - If value_or_var is a Signal -> return as-is
    - If it's a Tk var -> wrap via factory.from_var(var)
    - Else -> create new Signal(default or value_or_var)
    """
from ttkbootstrap_next.signals import Signal  # avoid import cycles

if hasattr(value_or_var, "__class__") and value_or_var.__class__.__name__ == "Signal":
    return value_or_var
if isinstance(value_or_var, _TK_VARS):
    return factory.from_var(value_or_var)
return factory(value_or_var if value_or_var is not None else default)
```

---

## 1) Base mixins (drop into your widget base)

```python

# compat_mixins.py

class CommandCompatMixin:


    """Wire legacy command= to v2 stream."""


def _apply_command_kw(self, kwargs, *, invoke_event="<<Invoke>>"):
    cmd = kwargs.pop("command", None)
    if cmd is not None:
        self.on(invoke_event).then_stop().listen(lambda e: cmd())


class VariableCompatMixin:


    """Accept textvariable=/variable= as Tk var or Signal, then plumb into ttk."""


def _adopt_signal(self, *, option_name, kwargs, default):
    from ttkboostrap.signals import Signal
    from .signals_compat import to_signal

    var = kwargs.pop(option_name, None)
    sig = to_signal(var, default=default, factory=Signal)
    setattr(self, f"{option_name}_signal", sig)  # expose for v2 users
    super().configure(**{option_name: sig.name})  # Tcl var for ttk interop
    return sig

```

**Usage inside each widget `__init__`:**

```python
self._apply_command_kw(kwargs, invoke_event="<<Invoke>>")  # if widget has command
sig = self._adopt_signal(option_name="textvariable", kwargs=kwargs, default="")

# or: option_name="variable", default=False/0/...

```

> **Precedence:** if both a v2-native prop and `*variable=` are provided, let `*variable=` win (matches Tk). Log a
> one-line info/warn.

---

## 2) ttk widgets: per-class notes (minimum)

| Widget                                                   | Minimal compat steps                                                                                  |
|----------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| **Button**                                               | `command=` → `on("<<Invoke>>")`; support `image/compound` as-is; allow `textvariable` (Signal or Tk). |
| **Checkbutton**                                          | `command=` (toggle) → `on("<<Toggled>>")`; accept `variable=` (bool/int; Signal or Tk).               |
| **Radiobutton**                                          | `command=` on selection; accept shared `variable=` (value coercion as needed).                        |
| **Entry**                                                | Accept `textvariable=` (Signal/Tk). If `text=` present, create `Signal(text)` under the hood.         |
| **Combobox**                                             | Accept `textvariable=`. Optional: wire `postcommand=` to a stream if exposed; otherwise native.       |
| **Spinbox**                                              | Accept `textvariable=`. Optional: `command=` (increment) → `on("<<Spun>>")`.                          |
| **Scale**                                                | Accept `variable=` (double/int; Signal/Tk). Optional: `command=` sugar for continuous updates.        |
| **Progressbar**                                          | If supporting `variable=`, adopt it; else pure v2.                                                    |
| **Scrollbar**                                            | Pass-through; native `command`/`orient` as normal.                                                    |
| **Notebook**                                             | Keep v2 events only (e.g., `<<NotebookTabChanged>>`).                                                 |
| **Treeview**                                             | Keep v2 events only (e.g., `<<TreeviewSelect>>`).                                                     |
| **Separator / Frame / Labelframe / Panedwindow / Label** | No action; accept `textvariable=` on `Label`.                                                         |

**Sketch — Button**

```python
class Button(ttk.Button, CommandCompatMixin, VariableCompatMixin, BindingMixin):
    def __init__(self, master=None, **kwargs):
        self._apply_command_kw(kwargs, invoke_event="<<Invoke>>")
        if "textvariable" in kwargs or "text" in kwargs:
            self._adopt_signal(option_name="textvariable", kwargs=kwargs, default=kwargs.pop("text", ""))
        super().__init__(master, **kwargs)
```

**Sketch — Checkbutton**

```python
class Checkbutton(ttk.Checkbutton, CommandCompatMixin, VariableCompatMixin, BindingMixin):
    def __init__(self, master=None, **kwargs):
        self._apply_command_kw(kwargs, invoke_event="<<Toggled>>")
        self._adopt_signal(option_name="variable", kwargs=kwargs, default=False)
        super().__init__(master, **kwargs)
```

---

## 3) `Text` adapter (tk.Text)

Goals: optional **`textvariable`/Signal sync**, keep native API intact, bridge `<<Modified>>`.

```python
class Text(tk.Text, BindingMixin):
    def __init__(self, master=None, **kwargs):
        tv = kwargs.pop("textvariable", None)
        super().__init__(master, **kwargs)

        if tv is not None:
            from yourlib.signals import Signal
            from .signals_compat import to_signal
            self.text_signal = to_signal(tv, default="", factory=Signal)

            def pull_from_widget(_e=None):
                try:
                    v = self.get("1.0", "end-1c")
                    if v != self.text_signal():
                        self.text_signal.set(v)
                except Exception:
                    pass
                self.edit_modified(False)

            self.bind("<<Modified>>", pull_from_widget)
            self.edit_modified(False)  # reset

            # Signal → Text
            self.text_signal.subscribe(lambda v: self._set_if_changed(v))

    def _set_if_changed(self, v: str):
        cur = self.get("1.0", "end-1c")
        if cur != v:
            self.delete("1.0", "end")
            if v:
                self.insert("1.0", v)

```

> Add debounce for very large texts if needed.

---

## 4) `Canvas` adapter (tk.Canvas)

Minimum: **do nothing**—native API remains great. Optional sugar:

\`\`\`python
class Canvas(tk.Canvas, BindingMixin):

# Optional sugar: item_on(tag_or_id, sequence) -> Stream

def item_on(self, tag_or_id, sequence):
tag = str(tag_or_id)
return self.on(sequence, scope=tag)  # treat Tk tag as a "class" scope
\`\`\`

If that’s too much, skip it; the minimum is to leave `Canvas` untouched.

---

## 5) Docs: tiny migration table

| v1 / Tk idiom                             | v2 (with minimal compat)                                           |
|-------------------------------------------|--------------------------------------------------------------------|
| `Button(..., command=fn)`                 | Works; wired to `on("<<Invoke>>")`                                 |
| `Entry(..., textvariable=StringVar())`    | Works; wrapped as `Signal` and plumbed to ttk                      |
| `Checkbutton(..., variable=BooleanVar())` | Works; wrapped as `Signal`                                         |
| `Text(..., textvariable=StringVar())`     | Works; bi-directional sync via `<<Modified>>`                      |
| `Canvas` item bindings                    | Use native `.tag_bind(...)` or v2 events; no extra compat required |

---

## 6) What **not** to do (keeps scope tiny)

- No legacy `bootstyle` parser—require v2 builders for styles.
- No compat for `bind` getters (returning Tcl scripts).
- No global layout shims—layout remains v2 (`Grid/Pack` containers).

---

## Bottom line

- Implement **two base mixins** + **two adapters** (Text/Canvas).
- Wire `command=` and `*variable=` everywhere they historically exist.
- Keep everything else v2-native.

This preserves a clean architecture, offers high-impact compatibility, and keeps maintenance light for a solo
maintainer.
