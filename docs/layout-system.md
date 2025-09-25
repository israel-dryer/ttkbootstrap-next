# Layout system

The **ttkbootstrap** layout system introduces a two‑phase model—**describe** (stage intent) and **attach** (mount)—plus
**container
contexts** (`with Grid/Pack`) that collect children and flush them in order. It performs **smart method inference** (
pack/grid/place) and adds high‑level ergonomics on top of Tk: `Grid` with auto‑placement, dense fill, track config,
gaps, and sticky defaults; `Pack` with direction→side mapping, container‑level gaps, and item defaults; and `Place` via
`position="absolute|fixed"` with % and px helpers. Compared to plain Tk, you write less boilerplate, get consistent
spacing and defaults, and benefit from centralized validation and cleanup.

## How it works

### 1) Two phases: **describe** and **attach**

Every widget using `LayoutMixin` supports a **describe-only** phase and a **mount** phase.

- **Describe only** — `widget.layout_grid(...)/layout_pack(...)/layout_place(...)` or
  `widget.layout(..., merge=True|False)` just records the intended method and options on the widget. Nothing is mounted
  yet.
- **Attach** — `widget.attach(...)` resolves the effective method + options (considering the recorded layout and any
  overrides), picks the correct container adapter, validates options, and mounts via Tk (`grid/pack/place`) or a
  container’s `add(...)`.

This separation lets you (a) stage layout declaratively, (b) reuse/merge options safely, and (c) let the **container**
decide details at mount time.

### 2) Smart method inference

If you don’t specify a method, the mixin tries to infer it:

- `position="absolute"|"fixed"` ⇒ `place`
- On root (“.”) ⇒ default to `pack`
- If the container exposes a `preferred_layout_method()` (e.g., `Grid` returns `"grid"`, `Pack` returns `"pack"`), that
  wins.
- Heuristics based on container capabilities (`_mount_child_grid/_mount_child_pack`) and class names also apply.

### 3) Container contexts (the with-block flow)

The library keeps a tiny **container stack** so you can write:

```python
with Grid(rows=..., columns=...) as grid:
    Label(...).layout_grid(row=0, column=0)  # only described here
    Button(...).layout_grid(row=0, column=1)
# on __exit__, the container flushes and mounts queued children
```

- The context stack API—`push_container`, `pop_container`, `current_container`, `has_current_container`, and an optional
  `default_root`—lets `LayoutMixin.layout(...)` “register” the child with the active container immediately (still not
  mounted), so the container can validate and queue it. Mounting happens when the container **exits** the context (or
  immediately if no context is active).
- Both `Grid` and `Pack` implement this pattern: in `__enter__` they `attach()` themselves and push onto the stack; in
  `__exit__` they flush their queued children and pop.

### 4) Base container behavior

All layout containers derive from `BaseLayout`, which wraps a `ttk.Frame` and a style builder. It also exposes helpers
like `_mount_child_place` so absolute/overlay children can be placed onto the container’s surface. The base container’s
**preferred** method is `"pack"`; specific containers override this.

### 5) Grid container (features you don’t get in raw Tk)

`Grid` is a high-level wrapper around Tk’s `grid` with:

- **Auto-placement & dense fill**: `auto_flow='row'|'column'|'dense-row'|'dense-column'|'none'`. If you omit
  `row/column`, the container finds the next free slot; dense modes back-fill holes. Row/col spans are respected.
- **Configurable tracks**: `rows=` / `columns=` accept counts or spec lists (e.g., `"auto"` or `"24px"`), which are
  normalized to `rowconfigure/columnconfigure` weight & minsize.
- **Gaps and margins**: `gap` (per container) and child margins are normalized into `padx/pady`, applied only after the
  first row/column so the grid looks evenly spaced without manual math on each child.
- **Sticky defaults**: `sticky_items="nsew"` (or similar) becomes the default unless the child overrides.
- **Queue + flush**: children are validated/queued through `add(...)`/`register_layout_child(...)` and realized in FIFO
  order on flush.

`Grid.preferred_layout_method()` returns `"grid"`, which the mixin respects in inference.

### 6) Pack container (quality-of-life over raw Tk)

`Pack` wraps Tk’s `pack` with stack-like ergonomics:

- **Direction**: `'vertical'|'horizontal'|'row'|'column'|'-reverse'` map to `side` automatically; you can still override
  per item.
- **Gap**: container-level `gap` injects directional `padx/pady` **only after the first child**—no more remembering to
  set different paddings on each neighbor.
- **Item defaults**: `expand_items`, `fill_items`, `anchor_items` apply when the child omits them. Margins (
  `marginx/marginy`) are merged into external padding without clobbering any explicit `padx/pady`.
- Same queue/flush/context behavior as `Grid`. `Pack.preferred_layout_method()` is `"pack"`.

### 7) Place / absolute positioning

When a child’s `position` is `"absolute"` or `"fixed"`, the mixin routes to `place` and supports **percent-based**
dims (`relx/rely/relwidth/relheight`) and pixel offsets. If `"fixed"`, the widget places relative to its own master;
otherwise it will place **in** the target container surface.

### 8) Root behavior and fallbacks

If you attach directly to the root (the widget whose string name is `"."`) and the target is effectively “pack-like,”
the mixin sets sensible defaults (`fill='both', expand=True`) and packs it, so top-level layout “just works.”

---

## Key differences vs plain Tk

| Area                    | Plain Tk/Ttk                                                                 | This library                                                                                                     |
|-------------------------|------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| API shape               | You call `pack/grid/place` on each child directly; no staging                | **Two-phase**: `layout(...)` (describe) → `attach(...)` (mount), with option merging and method inference        |
| Container orchestration | No notion of an active container; you micromanage parents                    | **Context stack** (`with ...:`): children declared inside are registered/validated and mounted on exit           |
| Method choice           | You decide `pack` vs `grid` vs `place` everywhere                            | **Inference** via `position`, root checks, container’s `preferred_layout_method()`, and capabilities             |
| Grid features           | Manual placement; no holes-aware autoplace; hand-tuned padding               | **Auto-placement** (row/column/dense), **gap** on non-first rows/cols, **sticky defaults**, margin normalization |
| Pack features           | You must choose `side`, compute neighbor padding, set expand/fill repeatedly | **Direction → side** mapping, **container-level gap**, **item defaults**, and **margin merging**                 |
| Place features          | Raw `place(...)` with pixels/rel* you hand-wire                              | `position="absolute                                                                                              |fixed"` + helper that converts %, px, offsets, and targets container surface appropriately |
| Validation & safety     | Typos in options fail at runtime, scattered                                  | Centralized **option validation** per method before mounting; errors have hints/codes                            |
| Root convenience        | Easy to forget `expand/fill`                                                 | Root “pack on attach” adds sensible defaults for top-level containers                                            |

---

### Quick, idiomatic examples

#### Declarative grid with autoplacement + gap

```python
with Grid(columns=[1, 1, 1], gap=8, padding=12, sticky_items="nsew") as g:
    Label(text="A").layout_grid()  # auto-placed
    Label(text="B").layout_grid(columnspan=2)  # spans; dense packing fills holes
    Button(text="OK").layout_grid()
```

(Children are queued and mounted when the context exits.)

#### Vertical stack with defaults and margins

```python
with Pack(direction="vertical", gap=12, expand_items=True, fill_items="x") as p:
    Label(text="Title").layout_pack(marginy=8)
    Entry().layout_pack()
    Button(text="Save").layout_pack(anchor="e")  # overrides the default anchor
```

(Gap applied only between siblings after the first; margins merged with padding.)

#### Absolute overlay inside a container

```python
with Grid(padding=16) as g:
    Canvas(width=300, height=200).layout_grid(row=0, column=0)
    Label(text="Overlay").layout_place(x="50%", y="50%", anchor="center")
```

(Place uses `%` → `relx/rely`, honors `xoffset/yoffset`, and places **in** the container surface.)

---

### Mental model recap

1) **Describe** each child’s intent; 2) **Containers** collect + validate those intents while they are active in a
   `with` block; 3) On **flush**, containers translate intents into precise Tk geometry calls (grid/pack/place), adding
   quality-of-life features—**autoplacement, gaps, defaults, margins**, and **method inference**—so you ship polished
   layouts with far less boilerplate.
