# Typography Design Document

## Overview

This document defines a consistent typographic system based on **Bootstrap 5** conventions, translated into **Tkinter
font settings**. It provides a scalable font mapping using semantic styles such as `display-1`, `h1`, `body`, and
`small`, compatible with both named font tuples and programmatic font retrieval via a helper class.

---

## Bootstrap-to-Tkinter Typography Mapping

| Style       | Bootstrap Size (rem) | Approx px | Tkinter Font Tuple         |
|-------------|----------------------|-----------|----------------------------|
| `display-1` | 5                    | 80px      | `("Segoe UI", 32, "bold")` |
| `display-2` | 4.5                  | 72px      | `("Segoe UI", 28, "bold")` |
| `display-3` | 4                    | 64px      | `("Segoe UI", 24, "bold")` |
| `display-4` | 3.5                  | 56px      | `("Segoe UI", 22, "bold")` |
| `display-5` | 3                    | 48px      | `("Segoe UI", 20, "bold")` |
| `display-6` | 2.5                  | 40px      | `("Segoe UI", 18, "bold")` |
| `h1`        | 2.5                  | 40px      | `("Segoe UI", 18, "bold")` |
| `h2`        | 2                    | 32px      | `("Segoe UI", 16, "bold")` |
| `h3`        | 1.75                 | 28px      | `("Segoe UI", 14, "bold")` |
| `h4`        | 1.5                  | 24px      | `("Segoe UI", 12, "bold")` |
| `h5`        | 1.25                 | 20px      | `("Segoe UI", 11, "bold")` |
| `h6`        | 1                    | 16px      | `("Segoe UI", 10, "bold")` |
| `body`      | 1                    | 16px      | `("Segoe UI", 10)`         |
| `small`     | 0.875                | 14px      | `("Segoe UI", 9)`          |

---

## Typography Helper Class (Python)

```python
from tkinter import font


class Typography:
    def __init__(self, family="Segoe UI"):
        self.family = family

    def get(self, style: str):
        mapping = {
            "display-1": (self.family, 32, "bold"),
            "display-2": (self.family, 28, "bold"),
            "display-3": (self.family, 24, "bold"),
            "display-4": (self.family, 22, "bold"),
            "display-5": (self.family, 20, "bold"),
            "display-6": (self.family, 18, "bold"),
            "h1": (self.family, 18, "bold"),
            "h2": (self.family, 16, "bold"),
            "h3": (self.family, 14, "bold"),
            "h4": (self.family, 12, "bold"),
            "h5": (self.family, 11, "bold"),
            "h6": (self.family, 10, "bold"),
            "body": (self.family, 10),
            "small": (self.family, 9),
        }
        return mapping.get(style, (self.family, 10))

# Example Usage:
# label = ttk.Label(root, text="Heading", font=Typography().get("h1"))
```

---

## Tkinter Default Named Fonts

| Named Font             | Purpose                      | Typical Windows Value     |
|------------------------|------------------------------|---------------------------|
| `"TkDefaultFont"`      | General widgets, labels      | `("Segoe UI", 9)`         |
| `"TkTextFont"`         | Text widgets (Text, Message) | `("Courier New", 10)`     |
| `"TkHeadingFont"`      | Treeview headers             | `("Segoe UI", 9, "bold")` |
| `"TkMenuFont"`         | Menu items                   | `("Segoe UI", 9)`         |
| `"TkCaptionFont"`      | Caption text                 | `("Segoe UI", 9)`         |
| `"TkSmallCaptionFont"` | Rarely used (e.g., dialogs)  | `("Segoe UI", 8)`         |
| `"TkIconFont"`         | Icon labels                  | `("Segoe UI", 8)`         |
| `"TkTooltipFont"`      | Tooltip (if supported)       | `("Segoe UI", 8)`         |

You can modify these fonts globally using:

```python
import tkinter.font as tkfont

tkfont.nametofont("TkDefaultFont").configure(size=10)
```

---

## Bootstrap-to-Tkinter Named Font Mapping Summary

| Bootstrap Style  | Bootstrap px | Closest Tkinter Font              | Notes                                     |
|------------------|--------------|-----------------------------------|-------------------------------------------|
| `display-1`      | \~80px       | custom `("Segoe UI", 32, "bold")` | No default font this large                |
| `h1`             | \~40px       | custom `("Segoe UI", 18, "bold")` | Must be manually defined                  |
| `body`           | \~16px       | `TkDefaultFont`                   | Equivalent to base body text              |
| `small`          | \~14px       | `TkSmallCaptionFont` or custom    | Often overridden with 8–9pt font manually |
| `menu` text      | \~14–16px    | `TkMenuFont`                      | Close to body or small text               |
| Treeview heading | \~16px       | `TkHeadingFont`                   | Used for header-like roles                |

---

## Summary

* This document defines a font scale in **Tkinter** that emulates **Bootstrap 5 typography**.
* All heading levels and display styles are available via the `Typography` class.
* Tkinter’s named fonts serve well for base `body` and `small` styles.
* Large display styles should be defined manually as Tkinter does not include them by default.
* You can override named fonts globally for app-wide consistency.
