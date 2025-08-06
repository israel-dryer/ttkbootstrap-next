# ttkbootstrap Project Structure

```plaintext
ttkbootstrap/
├── __init__.py
├── app.py

├── common/                         # Shared types, utilities, logger
│   ├── __init__.py
│   ├── types.py
│   ├── logger.py
│   └── utils.py

├── core/                           # Foundational logic (internal)
│   ├── __init__.py
│   ├── _widget_base.py
│   └── _mixins/
│       ├── __init__.py
│       ├── binding.py
│       ├── configure.py
│       ├── container.py
│       ├── focus.py
│       ├── geometry.py
│       ├── grab.py
│       ├── icon.py
│       ├── layout.py
│       └── winfo.py

├── tkinterop/                      # Integration with Tkinter internals
│   ├── __init__.py
│   ├── commands.py
│   ├── aliases.py
│   ├── substitutions.py
│   └── types.py

├── signals/                        # Public reactive signal system
│   ├── __init__.py
│   └── signal.py

├── validation/                     # Input validation rules
│   ├── __init__.py
│   ├── rules.py
│   └── types.py

├── datasources/                    # Data backends
│   ├── __init__.py
│   ├── base.py
│   ├── sqlite_source.py
│   ├── web_source.py
│   ├── file_source.py
│   └── utils.py

├── routing/                         # User-facing routing
│   ├── __init__.py
│   ├── router.py
│   ├── views.py
│   └── types.py

├── images/                         # Image-related utilities
│   ├── __init__.py
│   ├── photo.py
│   ├── svg.py
│   ├── gif.py
│   ├── video.py
│   └── utils.py

├── icons/                          # Icon font management
│   ├── __init__.py
│   ├── bootstrap.py
│   ├── lucide.py
│   └── icon.py

├── assets/                         # Embedded static files (icons, themes, images)
│   ├── __init__.py
│   ├── icons/
│   │   ├── __init__.py
│   │   ├── bootstrap.json
│   │   ├── bootstrap.ttf
│   │   ├── lucide.json
│   │   └── lucide.ttf
│   ├── images/
│   │   └── __init__.py
│   └── themes/
│       ├── __init__.py
│       ├── dark.json
│       └── light.json

├── themes/                         # Theme styling and token system
│   ├── __init__.py
│   ├── theme.py
│   ├── style.py
│   ├── tokens.py
│   ├── element.py
│   ├── typography.py
│   ├── types.py
│   └── _style_builders/
│       ├── __init__.py
│       ├── badge.py
│       ├── base.py
│       ├── button.py
│       ├── canvas.py
│       ├── check_button.py
│       ├── entry.py
│       ├── frame.py
│       ├── icon_button.py
│       ├── label.py
│       ├── label_frame.py
│       ├── notebook.py
│       ├── paned_window.py
│       ├── progressbar.py
│       ├── radio_button.py
│       ├── scale.py
│       ├── scrollbar.py
│       ├── separator.py
│       ├── size_grip.py
│       ├── spinbox.py
│       ├── switch_button.py
│       └── window.py

├── layouts/                        # Layout container widgets
│   ├── __init__.py
│   ├── base.py
│   ├── frame.py
│   ├── grid_frame.py
│   ├── label_frame.py
│   ├── notebook.py
│   ├── pack_frame.py
│   ├── paned_window.py
│   ├── scrollbar.py
│   ├── separator.py
│   ├── size_grip.py
│   ├── layout_mixin.py
│   ├── layout_utils.py
│   └── types.py

├── composites/                     # Composite widgets (multiple parts)
│   ├── __init__.py
│   ├── list_item.py
│   └── simple_list_item.py

├── widgets/                        # Public widgets
│   ├── __init__.py
│   ├── types.py
│   ├── button.py
│   ├── check_button.py
│   ├── icon_button.py
│   ├── menu_button.py
│   ├── radio_button.py
│   ├── switch_button.py
│   ├── entry.py
│   ├── date_entry.py
│   ├── file_entry.py
│   ├── number_entry.py
│   ├── password_entry.py
│   ├── text_entry.py
│   ├── label.py
│   ├── listbox.py
│   ├── progressbar.py
│   ├── scale.py
│   ├── virtual_list.py
│   ├── canvas.py
│   ├── mixins/
│   │   ├── __init__.py
│   │   └── composite.py
│   └── _parts/
│       ├── __init__.py
│       ├── entry_field.py
│       ├── entry_field_helpers.py
│       └── number_spinbox_field.py

├── dialogs/                        # Dialog components (future)
│   └── __init__.py

├── exceptions/                     # Custom exception classes
│   └── __init__.py

├── localization/                   # Message translation system
│   ├── __init__.py
│   ├── message_catalog.py
│   └── messages.py
```

