# Integrated icons

The icon system renders crisp, theme‑aware icons from **vector icon fonts** (e.g., Lucide, Bootstrap) into Tk images on
demand—so you can say “give me a 20px ‘save’ icon in the current theme color,” and it just works.

## How it works

- **Icon classes per set.** `LucideIcon` and `BootstrapIcon` are small adapters over a common `Icon` base. Creating an
  icon initializes the set (loads the font + codepoint map) and renders the glyph.
- **Fonts & maps from package assets.** `Icon.initialize(icon_set)` pulls a TTF and a JSON codepoint map from your
  package resources, writes the font to a temp file, and configures the renderer. No external files to manage at
  runtime.
- **On‑demand rasterization with caching.** Given `(name, size, color, set)`, the renderer uses PIL to draw the glyph to
  an RGBA canvas and returns a Tk `PhotoImage`. Results are memoized, so repeated requests are free. Utilities can also
  create transparent placeholders when needed.
- **Lifecycle & cleanup.** `cleanup()` resets caches and deletes the temporary font file if present.

## Stateful, theme‑aware icons on widgets

Widgets that include `IconMixin` get **stateful icon behavior** for free:

- `widget.icon({"name": "heart"})` asks the widget’s style builder to **build stateful icon assets** (
  normal/hover/pressed/focus/disabled/selected) for the current theme.
- The mixin binds to high‑level widget events (ENTER/LEAVE/FOCUS/BLUR/CLICK/SELECTED) and swaps the image automatically.
- When the **theme changes**, `IconMixin` listens for it, rebuilds the assets, and applies the correct state image—no
  manual recoloring.
- Disabled state is handled centrally; images only update when the asset actually changes (avoids churn).

---

# Why this is better than “regular Tk + images”

| Concern                                        | Plain Tk/ttk + images                         | Integrated icons                                                         |
|------------------------------------------------|-----------------------------------------------|--------------------------------------------------------------------------|
| Asset management                               | Ship PNG/SVG per size, per color, per theme   | **One font + JSON map** per set; sizes/colors generated at runtime       |
| Theming (light/dark)                           | Duplicate assets or ad‑hoc recoloring         | Icons are **re‑rendered** in theme colors; auto‑rebuild on theme change  |
| States (hover/pressed/focus/disabled/selected) | Manually wire events and swap images          | `IconMixin` binds once and **swaps state images automatically**          |
| Crispness & scaling                            | Bitmaps blur when scaled                      | **Vector glyphs** rasterized exactly at requested size → always crisp    |
| Performance                                    | Many files in memory; manual cache discipline | **Keyed cache** on `(name,size,color,set)`; placeholders available       |
| Setup                                          | Manage file paths and formats                 | `Icon.initialize(set)` loads from **package resources**—no path juggling |
| Cleanup                                        | Easy to forget to free resources              | `cleanup()` wipes caches and removes temp font cleanly                   |

---

## Quick usage

```python
from ttkbootstrap_next.icons.lucide import LucideIcon
from ttkbootstrap_next.icons.bootstrap import BootstrapIcon
from ttkbootstrap_next import ttk

# Direct image for any Tk/ttk widget
save_img = LucideIcon("save", size=20, color="#2b6cb0").image
ttk.Button(root, text="Save", image=save_img, compound="left").pack()

# Widget-integrated (preferred; requires a widget subclass with IconMixin)
btn = ttk.Button(root, text="Favorite")
btn.configure(icon={"name": "heart"})  # stateful; auto colors via style/theme
btn.pack()
```

- The **direct** approach gives a ready `PhotoImage` you can attach to any widget.
- The **integrated** approach lets the widget manage **stateful icons** and **theme transitions** automatically via the
  style builder + `IconMixin`.

---

## Mental model

Icons are **themed glyphs**: you specify intent (name, size, color). The system turns that into a Tk image, caches it,
and keeps it **in sync with widget state and theme**. You focus on the UI, not on asset files, recoloring, or event
plumbing.
