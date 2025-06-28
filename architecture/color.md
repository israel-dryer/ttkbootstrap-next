# Bootstrap-Inspired Color Theming Strategy for Tkinter

## Overview

This document outlines a semantic and scalable color theming strategy for Tkinter applications, inspired by Bootstrap
5.3. The system uses structured JSON theme files and a Python `Color` class for intuitive access to color roles and
states. It supports light and dark modes, state-aware variants, and layering.

---

## Core Principles

* **Semantic Naming**: Colors are grouped by role (e.g., `primary`, `danger`, `body`) and use consistent state keys (
  `bg_hover`, `text_disabled`, etc.).
* **State Awareness**: Each color role includes default, hover, active, and disabled variants.
* **Light and Dark Modes**: Each theme defines a parallel structure for both `light` and `dark` modes.
* **Surface Layers**: Layered surfaces (`layer-0`, `layer-1`, `layer-2`) enable elevation-based UI composition.
* **Grayscale Palette**: Grays `gray_100` through `gray_900` provide neutral tones for borders, text, and surfaces.
* **Focus Ring Support**: An explicit focus color is defined to support accessibility and keyboard navigation.

---

## Theme File Structure

Each theme (`light.json`, `dark.json`) includes:

### Top-Level Keys:

* `body`: Background, text, and border for the main surface.
* `text`: Standard and muted text colors.
* `layers`: Layered surface backgrounds.
* `gray`: Grayscale palette.

### Role Definitions:

Each role (e.g. `primary`, `danger`) includes:

```json
"primary": {
"bg": "#0d6efd",
"bg_hover": "#0b5ed7",
"bg_active": "#0a58ca",
"bg_disabled": "#cfe2ff",
"text": "#ffffff",
"text_disabled": "#adb5bd",
"border": "#9ec5fe",
"border_hover": "#86b7fe",
"border_active": "#5c9fe8"
}
```

---

## Color Access via Python Class

A `Color` class loads the theme and provides named tuple access:

```python
color = Color(mode="light")
button.configure(bg=color.primary.bg, fg=color.primary.text)
```

Supports theme switching via:

```python
color.switch("dark")
```

---

## File Structure

* `assets/light.json`
* `assets/dark.json`
* `color.py` (contains `Color` class)

---

## Benefits

* 🔁 Easy theme switching
* 🎯 Clean semantic access to role/state combinations
* 🌙 Full light/dark mode support
* 🧩 Compatible with custom Tkinter widget styling and canvas drawing

---

## Future Extensions

* Typography tokens
* Elevation tokens with transparency blending
* Custom user themes with overrides
* Automatic contrast checking for accessibility
