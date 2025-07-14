from typing import Literal, Union

EVENT_ALIASES = {
    # --- Mouse Events ---
    "click": "<Button-1>",
    "right_click": "<Button-3>",
    "middle_click": "<Button-2>",
    "dbl_click": "<Double-Button-1>",
    "drag": "<B1-Motion>",
    "wheel": "<MouseWheel>",
    "hover": "<Enter>",
    "leave": "<Leave>",
    "mouse_down": "<ButtonPress>",
    "mouse_up": "<ButtonRelease>",

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
    "combobox_selected": "<<ComboboxSelected>>",
    "menu_select": "<<MenuSelect>>",  # used in Menus
    "activate": "<<Activate>>",  # used in Notebooks
    "increment": "<<Increment>>",  # used in Spinbox
    "decrement": "<<Decrement>>",
    "deactivate": "<<Deactivate>>",
    "selection": "<<Selection>>",  # listbox, text selection
    "theme_changed": "<<ThemeChanged>>",  # ttk theme changed
    "input_method_changed": "<<IMChanged>>",
    "invalid": "<<Invalid>>",  # input validation
    "valid": "<<Valid>>",  # input validation
    "validated": "<<Validated>>",  # input validation
    "treeview_select": "<<TreeviewSelect>>"
}

# Type-safe alias
EventAlias = Literal[
    # Mouse Events
    "click",
    "right_click",
    "middle_click",
    "dbl_click",
    "drag",
    "wheel",
    "hover",
    "leave",
    "mouse_down",
    "mouse_up",

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
    "combobox_selected",
    "menu_select",
    "activate",
    "deactivate",
    "selection",
    "theme_changed",
    "input_method_changed",
    "increment",
    "decrement",

        # validation events
    "valid",
    "invalid",
    "validated",

        # Treeview events
    "treeview_select"
]

# Optional: allow raw sequences too
EventType = Union[EventAlias, str]
