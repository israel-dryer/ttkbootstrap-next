# Repository Guidelines

## Project Structure & Module Organization
- Source code lives in `src/ttkbootstrap`. Key areas: `core/` (widget base + mixins), `widgets/` (public widgets), `layouts/`, `style/`, `icons/`, `assets/` (themes, images, fonts), `interop/` (Tk interop), `signals/`, `validation/`, and `localization/`.
- Tests and demos are in `tests/` (e.g., `tests/demo_button.py`).
- Docs are in `docs/`; design notes in `architecture/`.

## Build, Test, and Development Commands
- Create env and install (editable):
  - `python -m venv .venv && .venv\Scripts\activate` (Windows)
  - `pip install -r requirements.txt`
  - `pip install -e .`
- Run demos locally: `python tests\demo_button.py` (or any `tests/demo_*.py`).
- Run tests (if added): `pytest -q`.
- Build distributions: `python -m pip install --upgrade build` then `python -m build` → artifacts in `dist/`.
- Quick import check: `python -c "import ttkbootstrap, sys; print(ttkbootstrap.__version__)"`.

## Coding Style & Naming Conventions
- Python 3.13+. Use type hints and docstrings for public APIs.
- Indentation: 4 spaces; keep lines readable (~100 chars).
- Naming: modules `snake_case.py`, classes `CamelCase`, functions/vars `snake_case`, constants `UPPER_SNAKE_CASE`.
- Imports: stdlib, third‑party, then local (grouped, alphabetized).
- Follow existing patterns in `src/ttkbootstrap/core/` and `src/ttkbootstrap/widgets/`.

## Testing Guidelines
- Prefer `pytest` with files named `tests/test_*.py` and descriptive test names.
- Cover new widgets/utilities with minimal, focused tests; add screenshot or demo updates for visual widgets.
- Run `pytest -q` locally; aim to keep tests headless where possible.

## Commit & Pull Request Guidelines
- Commits: imperative, present tense and scoped (e.g., `widgets: add number_entry step control`).
- PRs must include: brief description, rationale, before/after screenshots for UI changes, usage examples, and updated docs when relevant.
- Link related issues (e.g., `Closes #123`). Keep diffs minimal and focused.

## Security & Release Notes
- Do not commit secrets. Publishing uses `publish.bat` and Twine; set `TWINE_USERNAME=__token__` and `TWINE_PASSWORD` in your shell.
- Versioning is managed by `setuptools-scm`; do not edit `__version__` manually. Build artifacts land in `dist/`.

