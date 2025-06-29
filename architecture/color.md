# Color Theming Strategy for Tkinter

## Overview

This document defines a scalable and semantically rich color theming strategy for Tkinter applications, inspired by the **Fluent 2 Design System**. It leverages **flat camelCase token mappings** to represent foregrounds, backgrounds, strokes, and semantic roles like `brand`, `neutral`, and `status`. The system supports light, dark, and high contrast themes using a unified naming and loading strategy.

---

## Core Principles

* **Token-Based Design**: Each color is referenced via a flat, camelCase token such as `primaryButtonHoverBackground`.
* **State Awareness**: Stateful variants (`hover`, `pressed`, `disabled`, `focus`, etc.) are built directly into token names.
* **Neutral & Surface Layers**: Background layering is expressed via tokens like `calendarBackground`, `teachingBubbleRestBackground`, and others.
* **Role-Based Semantics**: Tokens cover interaction roles such as `primaryButton`, `dangerButton`, `checkBox`, and `statusBar`.
* **Accessibility Support**: Tokens like `controlOutlinesFocus`, `textDisabled`, and `sliderActiveDisabledBackground` support inclusive design.
* **Cross-Theme Consistency**: All themes expose the same token names with values adapted to the current theme variant.

---

## Token Format

Themes are represented as flat JSON mappings using camelCase keys:

```json
{
  "background": "#1b1a19",
  "primaryButtonHoverBackground": "#106EBE",
  "primaryButtonPressedText": "#FFFFFF",
  "statusBarBorderWarning": "#4F2A0F",
  "textHyperlink": "#2899f5",
  "checkBoxRestHoverText": "#FAF9F8"
}
```

All theme modes (light, dark, high contrast) use the **same token names** but assign different color values for optimal contrast and expression.

---

## Python Access Model

Color themes are accessed through a `ColorTheme` class which wraps token dictionaries and provides strongly typed properties:

```python
from theme_loader import load_json  # your custom JSON loader

class ColorTheme:
    def __init__(self, tokens: dict):
        self.tokens = tokens

    def get(self, name: str) -> str:
        return self.tokens.get(name, "#000000")

    @property
    def primary_button_hover_background(self) -> str:
        return self.tokens.get("primaryButtonHoverBackground", "#000000")

# Example usage
tokens = load_json("Fluent2AzureLightTokens.json")
theme = ColorTheme(tokens)
print(theme.primary_button_hover_background)
```

Properties mirror the camelCase tokens defined in the JSON files, but use Python-style snake\_case naming to access them conveniently.

---

## Theme Files

Color themes should be stored as flat `.json` files under a project directory such as `assets/` or `ttkbootstrap/assets/themes`. Examples:

* `assets/Fluent2AzureLightTokens.json`
* `assets/Fluent2AzureDarkTokens.json`
* `assets/Fluent2AzureHighContrastLightTokens.json`
* `assets/Fluent2AzureHighContrastDarkTokens.json`

Each file should:

* Use camelCase token names matching the `ColorTheme` class
* Contain only valid 6-digit hex values (no `rgba()`, no `BaseColors.*`)
* Include all required keys used in the application

---

## Benefits

✅ **Consistent access pattern** across all themes
🌗 **Seamless light/dark/high-contrast switching**
🔍 **Semantic, accessible, and designer-aligned**
🎯 **Direct integration with Canvas and ttk styling**
🧠 **Self-documenting through Python property mapping**
🌍 **Fluent Design-compatible**

---

## Future Extensions

* Custom token aliasing or overrides per application
* Layered surface management with background elevation
* Runtime color blending utilities for dynamic rendering
* Developer-facing theme visualizer
* Integration of **typography tokens** for font and scale control
