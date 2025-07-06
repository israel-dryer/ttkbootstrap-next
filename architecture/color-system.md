## 🎨 Color System Overview

This UI framework provides a structured and semantic color system designed for clarity, consistency, and flexibility
across themes and components. It is divided into several **logical categories** to make it easy to choose the right
color for the right purpose.

---

### ✅ 1. **Semantic Colors**

These are general-purpose colors named by their *intent*, not their hue.

```text
'primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark'
```

Use these for:

* Buttons
* Icons
* Alerts
* Emphasized text

> Example: `Button(color="primary")`, `Label(foreground="success")`

---

### 🌫 2. **Subtle Variants**

Soft, desaturated versions of the semantic colors. Ideal for **backgrounds**, **fills**, or **low-contrast UI elements
**.

```text
'primary-subtle', 'secondary-subtle', ..., 'base-subtle'
```

Use these when you want color without drawing too much attention.

---

### 🧱 3. **Layer Colors**

Predefined background layers for elevation and surface depth.

```text
'layer-1' → base surface  
'layer-5' → highest elevation
```

Use these for cards, modals, and stacking UI elements where depth or separation is needed.

---

### 🛠 4. **Utility Colors**

Basic global colors used for page-level theming and contrast.

```text
'foreground', 'background'
```

* `foreground`: default text or icon color
* `background`: page or root container background

---

### 🌈 5. **Color Shades by Hue**

Fine-grained control using traditional hue-based palettes. Each shade is available from `100` (lightest) to `900` (
darkest).

Examples:

```text
'blue-100', ..., 'blue-900'
'gray-100', ..., 'gray-900'
'purple-100', ..., 'purple-900'
...
```

Use these for:

* Charts
* Brand customization
* Accent or decorative styling
* Tailored theming beyond semantic roles

---

## 💡 When to Use What?

| Goal                                           | Use                   |
|------------------------------------------------|-----------------------|
| Communicate purpose (e.g., “success”, “error”) | ✅ **Semantic colors** |
| Provide soft background fills                  | ✅ **Subtle variants** |
| Build layered UIs (e.g., cards, modals)        | ✅ **Layer colors**    |
| Set universal text/background                  | ✅ **Utility colors**  |
| Customize with hue + intensity                 | ✅ **Color shades**    |

---

## 🧩 Composability

These color tokens are used throughout the framework in:

* `Button(color="primary")`
* `Label(foreground="gray-800")`
* `Container(background="layer-2")`
* `Surface(bg="blue-100")`

They are internally mapped to theme-specific values for light/dark support and branding consistency.
