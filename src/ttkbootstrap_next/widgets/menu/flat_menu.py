"""Flat menu implementation using Toplevel windows.

This provides a completely flat menu appearance with no native borders,
unlike native tk.Menu widgets which always have 3D borders on Windows.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, Dict, Any, Union


class FlatMenuItem(tk.Frame):
    """A single menu item in a flat menu."""

    def __init__(
        self,
        parent,
        label: str = "",
        command: Optional[Callable] = None,
        submenu: Optional['FlatMenu'] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.label_text = label
        self.command = command
        self.submenu = submenu
        self._hover = False

        # Get theme colors
        self.bg_color = '#212529'
        self.fg_color = '#f8f9fa'
        self.hover_color = '#343a40'

        # Configure frame
        self.configure(
            bg=self.bg_color,
            height=28,
            cursor='hand2'
        )

        # Create label
        self.label = tk.Label(
            self,
            text=label + (" ►" if submenu else ""),
            bg=self.bg_color,
            fg=self.fg_color,
            anchor='w',
            padx=16,
            pady=4,
            font=('Segoe UI', 10),
            width=20  # Minimum width in characters
        )
        self.label.pack(fill='both', expand=True, side='left')

        # Bind events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.label.bind('<Enter>', self._on_enter)
        self.label.bind('<Leave>', self._on_leave)
        self.label.bind('<Button-1>', self._on_click)

    def _on_enter(self, event=None):
        """Handle mouse enter."""
        self._hover = True
        self.configure(bg=self.hover_color)
        self.label.configure(bg=self.hover_color)

        # Show submenu if exists
        # Also ensure only the relevant child submenu (if any) remains open.
        menu_toplevel = self.winfo_toplevel()
        if hasattr(menu_toplevel, '_hide_child_menus'):
            if self.submenu is not None:
                menu_toplevel._hide_child_menus(except_menu=self.submenu)
                self.submenu.show_at_item(self)
            else:
                # Hovering a non-cascade item should close any open child submenus
                menu_toplevel._hide_child_menus()

    def _on_leave(self, event=None):
        """Handle mouse leave."""
        self._hover = False
        self.configure(bg=self.bg_color)
        self.label.configure(bg=self.bg_color)

    def _on_click(self, event=None):
        """Handle click."""
        # If this is a cascade item, clicking should open (or keep open) its submenu
        if self.submenu is not None:
            menu_toplevel = self.winfo_toplevel()
            if hasattr(menu_toplevel, '_hide_child_menus'):
                menu_toplevel._hide_child_menus(except_menu=self.submenu)
            self.submenu.show_at_item(self)
        elif self.command:
            # Hide all menus and execute command
            widget = self.winfo_toplevel()
            if hasattr(widget, '_hide_all'):
                widget._hide_all()
            self.command()


class FlatCheckMenuItem(tk.Frame):
    """A checkbutton menu item in a flat menu."""

    def __init__(
        self,
        parent,
        label: str = "",
        variable: Optional[tk.BooleanVar] = None,
        onvalue: Any = True,
        offvalue: Any = False,
        command: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.label_text = label
        self.variable = variable or tk.BooleanVar()
        self.onvalue = onvalue
        self.offvalue = offvalue
        self.command = command
        self._hover = False

        # Get theme colors
        self.bg_color = '#212529'
        self.fg_color = '#f8f9fa'
        self.hover_color = '#343a40'

        # Configure frame
        self.configure(
            bg=self.bg_color,
            height=28,
            cursor='hand2'
        )

        # Create checkmark label
        self.check_label = tk.Label(
            self,
            text="",
            bg=self.bg_color,
            fg=self.fg_color,
            width=2,
            font=('Segoe UI', 10)
        )
        self.check_label.pack(side='left')

        # Create text label
        self.label = tk.Label(
            self,
            text=label,
            bg=self.bg_color,
            fg=self.fg_color,
            anchor='w',
            padx=8,
            pady=4,
            font=('Segoe UI', 10)
        )
        self.label.pack(fill='both', expand=True, side='left')

        # Update checkmark
        self._update_check()

        # Bind events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.check_label.bind('<Enter>', self._on_enter)
        self.check_label.bind('<Leave>', self._on_leave)
        self.check_label.bind('<Button-1>', self._on_click)
        self.label.bind('<Enter>', self._on_enter)
        self.label.bind('<Leave>', self._on_leave)
        self.label.bind('<Button-1>', self._on_click)

        # Trace variable changes
        self.variable.trace_add('write', lambda *args: self._update_check())

    def _update_check(self):
        """Update the checkmark display."""
        if self.variable.get() == self.onvalue:
            self.check_label.configure(text="✓")
        else:
            self.check_label.configure(text="")

    def _on_enter(self, event=None):
        """Handle mouse enter."""
        self._hover = True
        self.configure(bg=self.hover_color)
        self.check_label.configure(bg=self.hover_color)
        self.label.configure(bg=self.hover_color)
        # Hovering a non-cascade item in a menu should close any open child submenus
        menu_toplevel = self.winfo_toplevel()
        if hasattr(menu_toplevel, '_hide_child_menus'):
            menu_toplevel._hide_child_menus()

    def _on_leave(self, event=None):
        """Handle mouse leave."""
        self._hover = False
        self.configure(bg=self.bg_color)
        self.check_label.configure(bg=self.bg_color)
        self.label.configure(bg=self.bg_color)

    def _on_click(self, event=None):
        """Handle click."""
        # Toggle value
        if self.variable.get() == self.onvalue:
            self.variable.set(self.offvalue)
        else:
            self.variable.set(self.onvalue)

        # Execute command if provided
        if self.command:
            self.command()


class FlatRadioMenuItem(tk.Frame):
    """A radiobutton menu item in a flat menu."""

    def __init__(
        self,
        parent,
        label: str = "",
        variable: Optional[Union[tk.StringVar, tk.IntVar]] = None,
        value: Any = None,
        command: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.label_text = label
        self.variable = variable
        self.value = value
        self.command = command
        self._hover = False

        # Get theme colors
        self.bg_color = '#212529'
        self.fg_color = '#f8f9fa'
        self.hover_color = '#343a40'

        # Configure frame
        self.configure(
            bg=self.bg_color,
            height=28,
            cursor='hand2'
        )

        # Create radio indicator label
        self.radio_label = tk.Label(
            self,
            text="",
            bg=self.bg_color,
            fg=self.fg_color,
            width=2,
            font=('Segoe UI', 10)
        )
        self.radio_label.pack(side='left')

        # Create text label
        self.label = tk.Label(
            self,
            text=label,
            bg=self.bg_color,
            fg=self.fg_color,
            anchor='w',
            padx=8,
            pady=4,
            font=('Segoe UI', 10)
        )
        self.label.pack(fill='both', expand=True, side='left')

        # Update radio indicator
        self._update_radio()

        # Bind events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.radio_label.bind('<Enter>', self._on_enter)
        self.radio_label.bind('<Leave>', self._on_leave)
        self.radio_label.bind('<Button-1>', self._on_click)
        self.label.bind('<Enter>', self._on_enter)
        self.label.bind('<Leave>', self._on_leave)
        self.label.bind('<Button-1>', self._on_click)

        # Trace variable changes
        if self.variable:
            self.variable.trace_add('write', lambda *args: self._update_radio())

    def _update_radio(self):
        """Update the radio indicator display."""
        if self.variable and self.variable.get() == self.value:
            self.radio_label.configure(text="●")
        else:
            self.radio_label.configure(text="○")

    def _on_enter(self, event=None):
        """Handle mouse enter."""
        self._hover = True
        self.configure(bg=self.hover_color)
        self.radio_label.configure(bg=self.hover_color)
        self.label.configure(bg=self.hover_color)
        # Hovering a non-cascade item in a menu should close any open child submenus
        menu_toplevel = self.winfo_toplevel()
        if hasattr(menu_toplevel, '_hide_child_menus'):
            menu_toplevel._hide_child_menus()

    def _on_leave(self, event=None):
        """Handle mouse leave."""
        self._hover = False
        self.configure(bg=self.bg_color)
        self.radio_label.configure(bg=self.bg_color)
        self.label.configure(bg=self.bg_color)

    def _on_click(self, event=None):
        """Handle click."""
        # Set value
        if self.variable:
            self.variable.set(self.value)

        # Execute command if provided
        if self.command:
            self.command()


class FlatSeparator(tk.Frame):
    """A separator line in a flat menu."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        sep_color = '#495057'

        self.configure(bg=sep_color, height=1)


class FlatMenu(tk.Toplevel):
    """A flat menu using Toplevel window - no borders!"""

    def __init__(self, parent=None, tearoff=False, **kwargs):
        # Don't show immediately
        super().__init__(parent)

        self.parent_menu = None
        self.parent_item = None
        self.items = []
        self.child_menus = []

        # Get theme colors
        self.bg_color = '#212529'
        self.border_color = '#495057'

        # Configure window for flat appearance
        self.withdraw()  # Hide initially
        self.overrideredirect(True)  # Remove window decorations
        self.configure(bg=self.border_color)  # Border color

        # Container for items with subtle border
        self.container = tk.Frame(self, bg=self.bg_color)
        self.container.pack(fill='both', expand=True, padx=1, pady=1)

        # Hover leave/enter semantics for submenu behavior
        # Close a submenu when the pointer leaves it (unless entering a descendant)
        self.bind('<Leave>', self._on_leave_window)
        self.bind('<Enter>', self._on_enter_window)

        # Track if menu is posted
        self._posted = False

        # Track global click bindings while posted
        self._click_bind_id1 = None
        self._click_bind_id3 = None
        self._motion_bind_id = None

        # Bind focus loss to hide
        self.bind('<FocusOut>', self._on_focus_out)

    def add_command(self, label: str = "", command: Optional[Callable] = None, **kwargs):
        """Add a command item to the menu."""
        item = FlatMenuItem(
            self.container,
            label=label,
            command=command
        )
        item.pack(fill='x', expand=True)
        self.items.append(item)
        return item

    def add_checkbutton(
        self,
        label: str = "",
        variable: Optional[tk.BooleanVar] = None,
        onvalue: Any = True,
        offvalue: Any = False,
        command: Optional[Callable] = None,
        **kwargs
    ):
        """Add a checkbutton item to the menu."""
        item = FlatCheckMenuItem(
            self.container,
            label=label,
            variable=variable,
            onvalue=onvalue,
            offvalue=offvalue,
            command=command
        )
        item.pack(fill='x', expand=True)
        self.items.append(item)
        return item

    def add_radiobutton(
        self,
        label: str = "",
        variable: Optional[Union[tk.StringVar, tk.IntVar]] = None,
        value: Any = None,
        command: Optional[Callable] = None,
        **kwargs
    ):
        """Add a radiobutton item to the menu."""
        item = FlatRadioMenuItem(
            self.container,
            label=label,
            variable=variable,
            value=value,
            command=command
        )
        item.pack(fill='x', expand=True)
        self.items.append(item)
        return item

    def add_separator(self, **kwargs):
        """Add a separator to the menu."""
        sep = FlatSeparator(self.container)
        sep.pack(fill='x', pady=4)
        self.items.append(sep)
        return sep

    def add_cascade(self, label: str = "", menu: Optional['FlatMenu'] = None, **kwargs):
        """Add a cascade (submenu) to the menu."""
        if menu:
            menu.parent_menu = self
            self.child_menus.append(menu)

        item = FlatMenuItem(
            self.container,
            label=label,
            submenu=menu
        )
        item.pack(fill='x', expand=True)
        self.items.append(item)

        if menu:
            menu.parent_item = item

        return item

    def post(self, x: int, y: int):
        """Show the menu at the specified position."""
        # Make sure we're hidden first
        if self._posted:
            self.unpost()

        # Update to calculate size while hidden
        self.update_idletasks()

        # Get required dimensions
        menu_width = max(self.container.winfo_reqwidth() + 2, 180)  # +2 for border
        menu_height = self.container.winfo_reqheight() + 2  # +2 for border

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Adjust position if off-screen
        final_x = x
        final_y = y

        if x + menu_width > screen_width:
            final_x = max(0, screen_width - menu_width - 10)
        if y + menu_height > screen_height:
            final_y = max(0, screen_height - menu_height - 10)

        # Show window first (required for proper positioning on Windows)
        self.deiconify()

        # Force update to ensure window is created
        self.update_idletasks()

        # Now set the geometry with absolute screen coordinates
        self.geometry(f"+{final_x}+{final_y}")
        self.geometry(f"{menu_width}x{menu_height}+{final_x}+{final_y}")

        self._posted = True

        # Lift to top and grab focus
        self.lift()
        self.focus_force()
        self.grab_set()

        # Bind global clicks to detect outside clicks
        self._bind_click_outside()


    def show_at_item(self, item: FlatMenuItem):
        """Show submenu next to the parent item."""
        if not self._posted:
            # Position to the right of parent item
            item.update_idletasks()
            item_x = item.winfo_rootx()
            item_y = item.winfo_rooty()
            item_width = item.winfo_width()

            # Show to the right of the item, aligned with top
            self.post(item_x + item_width - 2, item_y)

    def unpost(self):
        """Hide the menu."""
        self.withdraw()
        self._posted = False

        # Hide all child menus
        for child in self.child_menus:
            child.unpost()

        # Unbind global click handlers
        self._unbind_click_outside()

        # Release grab
        try:
            self.grab_release()
        except:
            pass


    def _hide_all(self):
        """Hide this menu and all parent menus."""
        self.unpost()
        if self.parent_menu:
            self.parent_menu._hide_all()


    def _hide_child_menus(self, except_menu: Optional['FlatMenu'] = None):
        """Hide this menu's direct child submenus, optionally keeping one open."""
        for child in list(self.child_menus):
            if child is except_menu:
                continue
            if getattr(child, '_posted', False):
                child.unpost()

    # --- Hover enter/leave helpers ---
    def _on_enter_window(self, event=None):
        # No-op placeholder; useful if future state needed
        pass

    def _on_leave_window(self, event=None):
        # Defer slightly to allow the pointer to settle on the next window
        if not self._posted:
            return
        self.after(80, self._check_hover_leave)

    def _check_hover_leave(self):
        if not self._posted:
            return
        try:
            x, y = self.winfo_pointerxy()
        except Exception:
            return

        # Only auto-close on hover-out for submenus (menus with a parent)
        if self.parent_menu is None:
            return

        # If pointer is inside this menu or any of its descendants, keep open
        if self._point_in_self_or_descendants(x, y):
            return

        # Otherwise, close this submenu
        self.unpost()

    def _point_in_self_or_descendants(self, x: int, y: int) -> bool:
        stack = [self]
        while stack:
            m = stack.pop()
            if getattr(m, '_posted', False):
                try:
                    if self._point_in_menu_bounds(m, x, y):
                        return True
                except Exception:
                    pass
            stack.extend(getattr(m, 'child_menus', []) or [])
        return False

    def _on_focus_out(self, event=None):
        """Handle focus loss - hide menu."""
        # Only hide if focus went outside menu tree
        if self._posted:
            self.after(100, self._check_hide)

    def _is_in_menu_tree(self, widget):
        """Check if a widget belongs to this menu or any child menu."""
        if widget is None:
            return False

        try:
            toplevel = widget.winfo_toplevel()

            # Check if it's this menu
            if toplevel == self:
                return True

            # Check if it's any child menu (recursively)
            for child in self.child_menus:
                if child._is_in_menu_tree(widget):
                    return True

            return False
        except:
            return False

    def _check_hide(self):
        """Check if we should hide the menu."""
        try:
            focused = self.focus_get()
            # Only hide if focus went outside the entire menu tree
            if not self._is_in_menu_tree(focused):
                self._hide_all()
        except:
            self._hide_all()

    # --- Outside click handling ---
    def _bind_click_outside(self):
        """Bind handlers to close menu when clicking outside.

        We bind to this Toplevel because a grab is set; all mouse clicks
        are delivered here, even when the pointer is outside. We use root
        coordinates to determine if the click occurred within any posted
        menu in this tree.
        """
        # Avoid duplicate bindings
        if self._click_bind_id1 or self._click_bind_id3 or self._motion_bind_id:
            return

        def handler(event):
            try:
                x = getattr(event, 'x_root', None)
                y = getattr(event, 'y_root', None)
                if x is None or y is None:
                    # Fallback to querying pointer if event lacks globals
                    x, y = self.winfo_pointerxy()

                # If the click is in any ancestor (parent) menu, close this submenu.
                if self._point_in_any_ancestor(x, y):
                    # Only close this branch, not the entire menu tree
                    self.unpost()
                    return

                # If the click is not in any menu at all, close the entire tree
                if not self._point_in_any_menu(x, y):
                    self._hide_all()
            except Exception:
                # On any error, ensure menus close to avoid getting stuck
                self._hide_all()

        # Store ids so we can unbind later
        self._click_bind_id1 = self.bind('<Button-1>', handler, add='+')
        self._click_bind_id3 = self.bind('<Button-3>', handler, add='+')

        # Motion handler to support switching between sibling cascades while a child holds grab
        def motion_handler(event):
            try:
                x = getattr(event, 'x_root', None)
                y = getattr(event, 'y_root', None)
                if x is None or y is None:
                    x, y = self.winfo_pointerxy()

                # If pointer inside this menu or any descendant, do nothing
                if self._point_in_self_or_descendants(x, y):
                    return

                # If pointer is within an ancestor menu, switch submenus accordingly
                self._handle_motion_over_ancestors(x, y)
            except Exception:
                # Ignore motion errors
                pass

        self._motion_bind_id = self.bind('<Motion>', motion_handler, add='+')

    def _unbind_click_outside(self):
        """Remove outside click handlers if present."""
        if self._click_bind_id1:
            try:
                self.unbind('<Button-1>', self._click_bind_id1)
            except Exception:
                pass
            finally:
                self._click_bind_id1 = None
        if self._click_bind_id3:
            try:
                self.unbind('<Button-3>', self._click_bind_id3)
            except Exception:
                pass
            finally:
                self._click_bind_id3 = None
        if self._motion_bind_id:
            try:
                self.unbind('<Motion>', self._motion_bind_id)
            except Exception:
                pass
            finally:
                self._motion_bind_id = None

    def _point_in_any_menu(self, x: int, y: int) -> bool:
        """Return True if the screen point (x, y) lies within this menu
        or any of its posted child menus."""
        # Walk up to the root menu
        root_menu = self
        while root_menu.parent_menu is not None:
            root_menu = root_menu.parent_menu

        # Depth-first traversal of posted menus
        stack = [root_menu]
        while stack:
            m = stack.pop()
            if getattr(m, '_posted', False):
                try:
                    if self._point_in_menu_bounds(m, x, y):
                        return True
                except Exception:
                    # Ignore measurement failures for hidden/withdrawn windows
                    pass
            # Recurse into children
            stack.extend(getattr(m, 'child_menus', []) or [])

        return False

    def _point_in_any_ancestor(self, x: int, y: int) -> bool:
        """Return True if point lies within any ancestor menu's bounds."""
        m = self.parent_menu
        while m is not None:
            try:
                if getattr(m, '_posted', False) and self._point_in_menu_bounds(m, x, y):
                    return True
            except Exception:
                pass
            m = m.parent_menu
        return False

    def _point_in_menu_bounds(self, m: 'FlatMenu', x: int, y: int) -> bool:
        """Check if point (x, y) lies within menu m's window bounds."""
        mx, my = m.winfo_rootx(), m.winfo_rooty()
        mw, mh = m.winfo_width(), m.winfo_height()
        return (mx <= x < mx + mw) and (my <= y < my + mh)

    def _handle_motion_over_ancestors(self, x: int, y: int):
        """While this submenu has the grab, handle pointer movement over
        ancestor menus to switch open cascades.

        - If pointer is over an ancestor menu's cascade item, open that submenu
          and close siblings.
        - If pointer is over ancestor menu but not over a cascade item, close
          the child submenus of that ancestor.
        """
        m = self.parent_menu
        while m is not None:
            if getattr(m, '_posted', False) and self._point_in_menu_bounds(m, x, y):
                item = self._find_cascade_item_at(m, x, y)
                if item is None:
                    m._hide_child_menus()
                else:
                    submenu = item.submenu
                    if submenu is not None:
                        m._hide_child_menus(except_menu=submenu)
                        submenu.show_at_item(item)
                break
            m = m.parent_menu

    def _find_cascade_item_at(self, menu: 'FlatMenu', x: int, y: int) -> Optional[FlatMenuItem]:
        for it in getattr(menu, 'items', []) or []:
            if isinstance(it, FlatMenuItem) and getattr(it, 'submenu', None) is not None:
                try:
                    ix, iy = it.winfo_rootx(), it.winfo_rooty()
                    iw, ih = it.winfo_width(), it.winfo_height()
                    if ix <= x < ix + iw and iy <= y < iy + ih:
                        return it
                except Exception:
                    pass
        return None

    # (Active root helpers removed)
