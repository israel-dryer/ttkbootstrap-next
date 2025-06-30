# Color Theming Strategy for Tkinter

## Overview

This document outlines a semantically rich and state-aware color theming strategy for Tkinter applications, inspired by
the **Bootstrap 5** color model and enhanced with dynamic theming logic. Themes are based on simple color tokens (e.g.,
`primary`, `danger`, `background`, `foreground`), from which **shades**, **states**, and **surface-layer variants** are
programmatically derived.

---

## Core Principles

* **Token Simplicity**: Themes are defined using flat tokens (e.g., `primary`, `info`, `background`, `foreground`) in
  camelCase or snake\_case.
* **State Derivation**: Colors for `hovered`, `pressed`, `disabled`, `focused`, etc. are automatically computed using
  tint/shade logic.
* **Semantic Layers**: Surface-related colors (e.g., `surfacePrimary`, `surfaceSubtle`, `onSurfacePrimary`) are derived
  based on context and theme mode.
* **Light/Dark Awareness**: The `ColorTheme` engine adjusts all derived values based on `mode` (`light` or `dark`).
* **Accessibility-Friendly**: Foreground-on-background contrast is calculated using WCAG-compliant contrast formulas.

---

## Theme Format

Themes are defined as JSON files like this:

```json
{
  "name": "light",
  "mode": "light",
  "colors": {
    "primary": "#0d6efd",
    "secondary": "#6c757d",
    "success": "#198754",
    "danger": "#dc3545",
    "info": "#0dcaf0",
    "warning": "#ffc107",
    "background": "#ffffff",
    "foreground": "#000000",
    "white": "#ffffff",
    "black": "#000000",
    "gray": "#adb5bd"
  }
}
```

Each token defines a base color used for role-based UI elements. No pre-shaded or state-specific variants are stored —
they are **generated at runtime**.

---

## Python Access Model

The `ColorTheme` class wraps a theme JSON object and provides:

* Direct access to tokens via `theme.color("primary")`
* Spectrum access via `theme.spectrum("primary")[600]`
* State-aware variants: `hovered()`, `pressed()`, `subtle()`, etc.
* Surface-level and foreground-access utilities: `on_surface()`, `surface_primary()`, etc.

### Example

```python
from ttkbootstrap.style.theme import ColorTheme, load_json

theme = ColorTheme(load_json("light.json"))
print(theme.hovered("primary"))  # shaded blue
print(theme.on_surface())  # "#fff" or "#000" based on contrast
print(theme.surface_subtle())  # lightly tinted background
```

### Function Naming

* `hovered(token)` → hover state color
* `pressed(token)` → pressed state color
* `focused(token)` → focus ring color
* `disabled(token)` → muted tone
* `on_surface()` → best contrast foreground for surface
* `surface_primary()` → base UI surface
* `surface_subtle()` → low emphasis surface
* `surface_emphasis()` → elevated surfaces (e.g., dialogs)

---

## Token Names and Derived Semantics

| Token Type     | Examples                           | Usage                                  |
|----------------|------------------------------------|----------------------------------------|
| Base Colors    | `primary`, `success`, `info`       | Buttons, indicators, semantic feedback |
| Grayscale      | `white`, `black`, `gray`           | General layout + contrast pairing      |
| Surface Colors | `background`, `foreground`         | Base UI background/text layers         |
| State Helpers  | `hovered()`, `pressed()`, etc.     | Auto-shaded/tinted per theme mode      |
| Surface Roles  | `surface_subtle()`, `on_surface()` | Derived layer styling                  |

---

## Theme Files

Stored as `.json` under a folder like `assets/themes/`:

* `light.json`
* `dark.json`

Each must include:

* `"mode"`: either `"light"` or `"dark"`
* `"colors"`: a dict of token names to hex values

No state variants need to be stored — they are **calculated** by `ColorTheme`.

---

## Benefits

- ✅ Minimal maintenance per theme file
- 🎨 Semantic roles + state coverage without duplication
- 🌗 Seamless switching between light/dark modes
- ♿ WCAG contrast-friendly text on surfaces
- 🧠 Self-documenting and extensible API
