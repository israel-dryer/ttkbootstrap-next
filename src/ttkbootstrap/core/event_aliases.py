from typing import Literal, Union

EVENT_ALIASES = {
    # --- Mouse Events ---
    "click": "<Button-1>",
    "right-click": "<Button-3>",
    "middle-click": "<Button-2>",
    "dbl-click": "<Double-Button-1>",
    "drag": "<B1-Motion>",
    "wheel": "<MouseWheel>",
    "hover": "<Enter>",
    "enter": "<Enter>",
    "leave": "<Leave>",
    "mouse-down": "<ButtonPress>",
    "mouse-up": "<ButtonRelease>",

    # --- Keyboard Events ---
    "keydown": "<KeyPress>",
    "keyup": "<KeyRelease>",
    "keydown.enter": "<KeyPress-Return>",
    "keyup.enter": "<KeyRelease-Return>",
    "keydown.esc": "<KeyPress-Escape>",
    "keyup.esc": "<KeyRelease-Escape>",
    "keydown.tab": "<KeyPress-Tab>",
    "keyup.tab": "<KeyRelease-Tab>",

    # --- Focus and Visibility ---
    "focus": "<FocusIn>",
    "blur": "<FocusOut>",
    "map": "<Map>",
    "unmap": "<Unmap>",
    "visibility": "<Visibility>",
    "expose": "<Expose>",
    "destroy": "<Destroy>",

    # --- General Input Aliases ---
    "return": "<Return>",
    "tab": "<Tab>",
    "escape": "<Escape>",

    # --- Motion & Resize ---
    "motion": "<Motion>",
    "configure": "<Configure>",  # widget resized or moved

    # --- Virtual Events (<<...>>) ---
    "changed": "<<Changed>>",
    "modified": "<<Modified>>",  # used with Text widgets
    "combobox-selected": "<<ComboboxSelected>>",
    "menu-selected": "<<MenuSelect>>",  # used in Menus
    "activate": "<<Activate>>",  # used in Notebooks
    "increment": "<<Increment>>",  # used in Spinbox
    "decrement": "<<Decrement>>",
    "deactivate": "<<Deactivate>>",
    "selected": "<<Selected>>",
    "deselected": "<<Deselected>>",
    "selection": "<<Selection>>",  # listbox, text selection
    "theme-changed": "<<ThemeChanged>>",  # ttk theme changed
    "input-method-changed": "<<IMChanged>>",
    "invalid": "<<Invalid>>",  # input validation
    "valid": "<<Valid>>",  # input validation
    "validated": "<<Validated>>",  # input validation
    "treeview-select": "<<TreeviewSelect>>"
}

# Type-safe alias
EventAlias = Literal[
    # Mouse Events
    "click",
    "right-click",
    "middle-click",
    "dbl-click",
    "drag",
    "wheel",
    "hover",
    "enter",
    "leave",
    "mouse-down",
    "mouse-up",

    # Keyboard Events
    "keydown",
    "keyup",
    "keydown.enter",
    "keyup.enter",
    "keydown.esc",
    "keyup.esc",
    "keydown.tab",
    "keyup.tab",

        # Focus and Visibility
    "focus",
    "blur",
    "map",
    "unmap",
    "visibility",
    "expose",
    "destroy",

        # General Key Aliases
    "return",
    "tab",
    "escape",

        # Motion & Resize
    "motion",
    "configure",

        # Virtual Events
    "changed",
    "modified",
    "combobox-selected",
    "menu-selected",
    "activate",
    "deactivate",
    "selected",
    "deselected",
    "selection",
    "theme-changed",
    "input-method-changed",
    "increment",
    "decrement",

        # validation events
    "valid",
    "invalid",
    "validated",

        # Treeview events
    "treeview-select"
]

# Optional: allow raw sequences too
EventType = Union[EventAlias, str]
