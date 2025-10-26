# Typography Design Document

## Overview

This document defines a consistent typographic system inspired by the **Fluent 2 Design System**, adapted for use in *
*Tkinter**. It provides a scalable font mapping using semantic style tokens (e.g., `display-xl`, `heading-md`,
`body-sm`), each of which maps directly to a Tkinter-compatible font tuple.

---

## Fluent-to-Tkinter Typography Mapping

| Token Name   | Font Size (px) | Weight | Tkinter Font Tuple         | Description                |
|--------------|----------------|--------|----------------------------|----------------------------|
| `display-xl` | 48             | Bold   | `("Segoe UI", 24, "bold")` | Hero display style         |
| `display-lg` | 40             | Bold   | `("Segoe UI", 20, "bold")` | Large section header       |
| `heading-xl` | 32             | Bold   | `("Segoe UI", 16, "bold")` | Page heading               |
| `heading-lg` | 28             | Bold   | `("Segoe UI", 14, "bold")` | Section heading            |
| `heading-md` | 24             | Bold   | `("Segoe UI", 12, "bold")` | Card or subheading         |
| `body-lg`    | 20             | Normal | `("Segoe UI", 11)`         | Large paragraph            |
| `body`       | 16             | Normal | `("Segoe UI", 10)`         | Default text               |
| `body-sm`    | 14             | Normal | `("Segoe UI", 9)`          | Small paragraph or caption |
| `label`      | 14             | Bold   | `("Segoe UI", 9, "bold")`  | Field or control label     |
| `caption`    | 12             | Normal | `("Segoe UI", 8)`          | Tooltip or metadata text   |

---

## Typography Helper Class (Python)

```python
class FluentTypography:
    def __init__(self, family="Segoe UI"):
        self.family = family

    def get(self, token: str):
        styles = {
            "display-xl": (self.family, 24, "bold"),
            "display-lg": (self.family, 20, "bold"),
            "heading-xl": (self.family, 16, "bold"),
            "heading-lg": (self.family, 14, "bold"),
            "heading-md": (self.family, 12, "bold"),
            "body-lg": (self.family, 11),
            "body": (self.family, 10),
            "body-sm": (self.family, 9),
            "label": (self.family, 9, "bold"),
            "caption": (self.family, 8),
        }
        return styles.get(token, (self.family, 10))

# Example Usage:
# label = ttk.Label(root, text="Title", font=FluentTypography().get("heading-lg"))
```

---

## Summary

* This document replaces the Bootstrap-style rem-based scale with Fluent 2–inspired semantic tokens.
* Each token corresponds to a single Tkinter font tuple.
* This consolidated approach respects the limitations of Tkinter while remaining semantically expressive.
* The `FluentTypography` class provides centralized access to typography tokens for consistent use throughout the app.
* Font family can be customized globally through the class constructor.
