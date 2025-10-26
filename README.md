# ttkbootstrap-next

> **Next-generation theming and layout engine for Tkinter**  
> Reimagining [`ttkbootstrap`](https://github.com/israel-dryer/ttkbootstrap) with a modern, declarative API, reactive
> event streams, and unified layout containers.

---

⚠️ **Project Status:**  
`ttkbootstrap-next` is currently **under active development** and preparing for its first public release.  
APIs are evolving rapidly, documentation is incomplete, and the package is **not yet available on PyPI**.  
If you’d like to follow development or contribute feedback, please ⭐ the repo and watch for announcements.

---

## 💡 Overview

`ttkbootstrap-next` is a full re-architecture of the original [
`ttkbootstrap`](https://github.com/israel-dryer/ttkbootstrap) library — a modern theming and layout framework built on
top of Tkinter’s classic `ttk` widgets.

This “Next” version explores a **cleaner, more expressive API** that embraces modern GUI design principles while
retaining full compatibility with Tk’s core concepts.

---

## ✨ Core Goals

- **Declarative Layouts**  
  Unified `PackFrame`, `GridFrame`, and `PageStack` containers with consistent `gap`, `margin`, and `sticky` options.

- **Modern Styling System**  
  Color and surface tokens (`surface`, `variant`, `fg/primary`, `bg/neutral`, etc.) inspired by design systems like
  Bootstrap 5 and Material 3.

- **Reactive Events**  
  A new Stream API for Tkinter events:
  ```python
  widget.on("<Button-1>").cancel_when(lambda e: e.data["id"] == 105).listen(handler)
  ```

- **Stateful Icons**  
  Dynamic icon registry that adapts to widget state (normal, hover, pressed, disabled, selected).

- **App Context Manager**  
  Cleaner structure using `App` as the root layout context:
  ```python
  from ttkbootstrap_next import App
  from ttkbootstrap_next.layouts import Pack
  from ttkbootstrap_next.widgets import Button

  with App("Demo") as app:
      with Pack(direction="vertical", gap=8, padding=16).attach(fill='both', expand=True):
          Button("Click me").attach()
  ```

- **Backwards Awareness**  
  Some portable features (e.g., style tokens, icon registry) will be backported to the classic library where feasible.

---

## 🧩 Relationship to Classic `ttkbootstrap`

| Classic (`ttkbootstrap`) | Next (`ttkbootstrap-next`)  |
|--------------------------|-----------------------------|
| Stable, production-ready | Experimental, in-progress   |
| Backwards-compatible API | Modern, declarative API     |
| Incremental updates and stable backports from `next` | Rapid iteration & new ideas |
| Available on PyPI        | Not yet released            |

Both projects will coexist:

- **`ttkbootstrap`** continues as the stable, widely used library.
- **`ttkbootstrap-next`** serves as the experimental playground for the next major generation.

---

## 🧱 Current Focus (Q4 2025)

- Completing the event Stream API testing
- Completing base widget set, including menus, windows, and dialogs
- Adding CLI tools for quick start
- Writing developer documentation and migration guide
- Preparing the first public preview (`v0.1.0`)

---

## 🚀 Development Setup

```bash
# Clone the repo
git clone https://github.com/israel-dryer/ttkbootstrap-next.git
cd ttkbootstrap-next

# (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# Install dependencies (if defined)
pip install -e .
```

---

## 🧪 Contributing

Contributions are welcome!  
This project is currently in **design and refactor phase**, so issues, API feedback, and discussion of layout ergonomics
are especially appreciated.

- Open issues for questions, bugs, or ideas.
- Pull requests should target the active development branch (`main` or `release-candidate-2.0` until launch).
- Please keep discussion focused on `ttkbootstrap-next` — feature requests for stable `ttkbootstrap` should go to that
  repo.

---

## 📜 License

Released under the [MIT License](LICENSE).

---

### 🗓️ Project Status

| Stage                   | Status | Notes                                         |
|-------------------------|:------:|-----------------------------------------------|
| Planning / Architecture |   ✅    | Core design completed                         |
| Layout Engine           |   ✅    | Layout engine completed                       |
| Event / Stream API      |   🚧   | Under test                                    |
| Style Tokens / Builders |  🏗️   | In progress...                                |
| Widgets                 |  🏗️   | In progress...                                |
| CLI Tools & Template    |   ⏳    | Coming soon                                   |
| Docs & Examples         |   ⏳    | Coming soon                                   |
| PyPI Release            |   ⏳    | Planned for initial public preview (`v0.1.0`) |

---

> © 2025 Israel Dryer — ttkbootstrap-next is part of the ttkbootstrap family of open-source projects.
