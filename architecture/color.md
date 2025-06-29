# Color Theming Strategy for Tkinter

## Overview

This document defines a scalable and semantically rich color theming strategy for Tkinter applications, inspired by the
**Fluent 2 Design System**. It leverages flat token mappings to represent foregrounds, backgrounds, strokes, and roles
like `brand`, `neutral`, and `status`. The system supports light, dark, and high contrast themes using a unified token
approach.

---

## Core Principles

* **Token-Based Design**: Each color is assigned a flat semantic token name such as `colorBrandBackgroundHover`.
* **State Awareness**: Stateful variants (hover, active, disabled) are built into token names.
* **Thematic Layers**: Neutral layers (`colorNeutralLayer1`, `colorNeutralLayerFloating`) support elevation and surface
  composition.
* **Brand & Status Roles**: Tokens cover brand (`colorBrandBackground`, `colorBrandForeground1`) and status use cases (
  `colorPaletteRedBackground3`).
* **Grayscale & Neutral Tones**: `colorNeutralForeground1`, `colorNeutralStroke1`, etc. provide system-wide neutral
  mappings.
* **Focus & Accessibility**: Dedicated tokens like `colorStrokeFocus2` and `colorNeutralForegroundDisabled` support
  keyboard navigation and accessibility.

---

## Token Format

Tokens follow the Fluent naming pattern:

```json
{
  "colorBrandBackground": "#0078D4",
  "colorBrandForegroundLink": "#016AFF",
  "colorNeutralBackground1": "#FFFFFF",
  "colorNeutralForegroundDisabled": "#C8C6C4",
  "colorPaletteRedBackground3": "#F1707B",
  "colorStrokeFocus2": "#605E5C"
}
```

All theme modes (light, dark, high contrast) use the same token names and remap values accordingly.

---

## Python Access Model

A `ColorTheme` class can load these tokens from a JSON file:

```python
class ColorTheme:
    def __init__(self, tokens: dict):
        self.tokens = tokens

    def get(self, name: str) -> str:
        return self.tokens.get(name, "#000000")


# Example
theme = ColorTheme(load_json("Fluent2AzureLightTokens.json"))
bg = theme.get("colorBrandBackgroundHover")
```

You may also wrap access with properties (e.g., `theme.brand_background_hover`).

---

## Theme Files

Each theme is stored as a flat JSON file of token-value pairs:

* `Fluent2AzureLightTokens.json`
* `Fluent2AzureDarkTokens.json`
* `Fluent2AzureHighContrastLightTokens.json`
* `Fluent2AzureHighContrastDarkTokens.json`

---

## Benefits

* 🌗 Unified token access across all themes
* 🔁 Seamless light/dark switching
* 🧠 Semantic, accessible, and scalable
* 🧩 Easy to bind to canvas elements or widget styles
* 🌍 Aligns with Fluent UI, Figma, and web platforms

---

## Future Extensions

* Support for custom token remapping
* Runtime blending for surface layers
* Visual token explorer for theme visualization
* Typography token integration
