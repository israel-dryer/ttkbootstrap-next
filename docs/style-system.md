# Style system

This style layer wraps `ttk.Style` with three big ideas:

1) **Composable builders** — A `StyleBuilderBase` assembles a full ttk style name from semantic options (surface, color,
   variant, size, theme) and only registers it if it doesn’t exist yet. It centralizes `configure`, `map`, `layout`, and
   element creation.

2) **Declarative layouts & image elements** — `Element` (for widget layout trees) and `ElementImage` (for stateful image
   backgrounds/borders) let you define a ttk style’s layout and per‑state imagery without hand‑writing raw
   `ttk.Style().layout(...)` tuples.

3) **Tokenized theming** — A `ColorTheme` object loads theme tokens (foreground/background, semantic colors, shade/tint
   spectra) and derives **hover/active/focus/disabled** states, contrast foregrounds, borders, elevation, and blends.
   Builders query the theme for colors—no hard‑coded hex needed.

A thin `Style` wrapper provides a fluent API over `ttk.Style` for theme switching plus `configure`, `map`, `layout`, and
element creation.

There’s also a **typography engine** that registers semantic named fonts (“display‑xl”, “heading‑md”, “body‑lg”, etc.)
and can override Tk’s default named fonts (`TkDefaultFont`, `TkTextFont`, …) so widgets pick up a consistent type scale
automatically.

---

## How a builder composes a style

A concrete builder (e.g., `ButtonStyleBuilder` for `TButton`) accepts semantic options like:

- `color='primary'`
- `variant='solid'|'outline'|'ghost'|'text'|'list'`
- `size='sm'|'md'|'lg'`
- `surface='background'` (or other surfaces)

The builder then:

- **Resolves a canonical ttk style name** by joining option values + surface + theme + target (e.g.,
  `primary.solid.md.background.light.TButton`). It only registers once; subsequent calls reuse it.
- **Derives colors from the theme** for `normal/hover/pressed/focus/disabled`, including contrast text and borders.
- **Creates/updates ttk elements** (e.g., a `… .border` image element) with stateful variants.
- **Defines the widget’s layout tree** (border → padding → label) with `Element`, then calls `Style.layout(...)`.
- **Configures and maps** final options (`foreground`, `background`, `padding`, `relief`, etc.) including state maps.

### Example: Button variants

`ButtonStyleBuilder` chooses a variant method (`build_default_style`, `build_outline_style`, `build_ghost_style`,
`build_text_style`, `build_list_style`, etc.), computes state colors from the current theme (including focus ring and
border), recolors assets per state, and maps icons to match the text color. Fonts are chosen via semantic names (`body`,
`body-lg`, etc.) so sizes scale predictably across `sm / md / lg`.

---

## Naming & existence

- `StyleBuilderBase.resolve_name()` constructs the ttk style string from option values + surface + theme + target.
- `exists()` and `build()` ensure **idempotent** registration: if already registered, the name is reused; otherwise,
  it’s created once and returned.

---

## Theme tokens & derived states

`ColorTheme` exposes:

- **Semantic tokens** (primary, success, warning, etc.) mapped to palette colors.
- **Derived interaction states**: `hover(color)`, `active(color)`, `focus(color)`, `focus_border(color)`,
  `focus_ring(color, surface)` that respect light/dark contrast.
- **Readability**: `on_color(color)` picks a text/icon foreground with adequate contrast.
- **Disabled & elevation** utilities for muted surfaces and layered backgrounds.

This keeps styles consistent without hard‑coding per‑widget colors.

---

## Typography (fonts as tokens)

`Typography` registers semantic named fonts and can override Tk’s defaults so any widget styled with “body‑lg”,
“heading‑md”, etc., uses a consistent, cross‑platform type ramp. Change a single token and styles update coherently.

---

# How this differs from plain Tk/ttk

| Topic              | Plain Tk/ttk                                         | This library                                                                                                          |
|--------------------|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Style naming       | Ad‑hoc strings like `"TButton"`, `"Primary.TButton"` | **Semantic, option‑driven** names composed by the builder (surface, color, variant, size, theme → one canonical name) |
| Register or reuse  | You manually track if a style exists                 | `build()` is **idempotent** and returns an existing style or registers once                                           |
| Colors             | You pick hex codes; per‑state variants are manual    | **Tokenized theme** provides hover/active/focus/disabled, borders, contrast text, elevation; coherent in light/dark   |
| Layout trees       | Nested tuples to `Style.layout(...)`                 | **Declarative `Element` trees** with `expand/side/sticky/border` helpers                                              |
| Image elements     | Hand‑build `element_create` args                     | `ElementImage` wraps state images, padding, borders, and arguments cleanly                                            |
| Configure & map    | Direct calls to `Style.configure()/map()`            | **Fluent wrapper** and builder helpers keep styling centralized and readable                                          |
| Interaction states | Define each state by hand                            | Builders compute and assign **all states** from theme utilities; consistent focus/border rules                        |
| Typography         | Use Tk named fonts case‑by‑case                      | **Semantic font tokens**, optional override of Tk defaults, single source for families/sizes/weights                  |

---

## Quick example: build & use a button style

```python
# Build (or reuse) a solid primary, md button on the default surface
style_name = ButtonStyleBuilder(
    color="primary",
    variant="solid",
    size="md",
    surface="background",
).build()

# Apply to a ttk.Button:
btn = ttk.Button(parent, text="Save", style=style_name)
```

- The builder constructs `Element`/`ElementImage` layout, recolors stateful assets, and configures/maps options.
- Switching the theme (e.g., light ↔ dark) recalculates derived colors and contrast; rebuilding styles keeps results
  coherent across modes.

---

## Mental model

Styles are **semantic recipes**: you declare intent (surface, variant, color, size), the builder asks the theme for
colors/typography, defines a small layout tree with state images, and emits a canonical ttk style name. No juggling hex
codes, state tables, or tuple layouts—**declare what you want; the builder and theme do the rest.**
