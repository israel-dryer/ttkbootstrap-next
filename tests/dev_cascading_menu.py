import tkinter as tk
from tkinter import ttk
import ctypes
import ctypes.wintypes

# Windows API constants
MF_BYPOSITION = 0x400
MIM_BACKGROUND = 0x00000002
MIM_APPLYTOSUBMENUS = 0x80000000

class MENUINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.wintypes.DWORD),
        ("fMask", ctypes.wintypes.DWORD),
        ("dwStyle", ctypes.wintypes.DWORD),
        ("cyMax", ctypes.wintypes.UINT),
        ("hbrBack", ctypes.wintypes.HBRUSH),
        ("dwContextHelpID", ctypes.wintypes.DWORD),
        ("dwMenuData", ctypes.c_void_p)
    ]

def get_menu_handle_from_window(hwnd, position):
    """Get submenu handle from window's menu bar by position"""
    # Get the menu bar
    hmenu = ctypes.windll.user32.GetMenu(hwnd)
    if not hmenu:
        print(f"Could not get menu bar")
        return None

    # Get submenu at position
    hsubmenu = ctypes.windll.user32.GetSubMenu(hmenu, position)
    if not hsubmenu:
        print(f"Could not get submenu at position {position}")
        return None

    print(f"Got submenu handle at position {position}: {hex(hsubmenu)}")
    return hsubmenu

def set_menu_background_by_handle(menu_handle, color_rgb):
    """
    Set the background color of a Windows native menu using its handle.
    menu_handle: HMENU handle
    color_rgb: tuple of (r, g, b) values 0-255
    """
    try:
        # Create a solid brush with the desired color
        # Windows uses BGR format (Blue, Green, Red)
        r, g, b = color_rgb
        color_ref = b | (g << 8) | (r << 16)
        hbrush = ctypes.windll.gdi32.CreateSolidBrush(color_ref)

        # Set up MENUINFO structure
        menu_info = MENUINFO()
        menu_info.cbSize = ctypes.sizeof(MENUINFO)
        menu_info.fMask = MIM_BACKGROUND | MIM_APPLYTOSUBMENUS
        menu_info.hbrBack = hbrush

        # Apply to menu
        result = ctypes.windll.user32.SetMenuInfo(menu_handle, ctypes.byref(menu_info))
        print(f"SetMenuInfo result: {result}")

        return result != 0
    except Exception as e:
        print(f"Error setting menu background: {e}")
        import traceback
        traceback.print_exc()
        return False

def set_menu_background(root_window, position, color_rgb):
    """
    Set the background color of a Windows native menu.
    root_window: the Tk root window
    position: position of the menu in the menu bar (0-indexed)
    color_rgb: tuple of (r, g, b) values 0-255
    """
    try:
        # Get the Windows HWND from the Tk window
        # winfo_id() returns a hex string on Windows that we need to convert
        tk_id = root_window.winfo_id()
        print(f"Tk window ID: {tk_id} ({hex(tk_id)})")

        # On Windows, we need to get the actual HWND
        # The Tk ID is actually the HWND on Windows
        hwnd = tk_id

        # Verify it's a valid window
        if not ctypes.windll.user32.IsWindow(hwnd):
            print(f"Not a valid window handle: {hwnd}")
            # Try getting parent
            hwnd = ctypes.windll.user32.GetParent(hwnd)
            print(f"Trying parent: {hwnd}")
            if not ctypes.windll.user32.IsWindow(hwnd):
                print("Parent also not valid")
                return False

        # Get the menu handle
        menu_handle = get_menu_handle_from_window(hwnd, position)
        if not menu_handle:
            return False

        return set_menu_background_by_handle(menu_handle, color_rgb)

    except Exception as e:
        print(f"Error setting menu background: {e}")
        import traceback
        traceback.print_exc()
        return False

root = tk.Tk()
root.geometry("800x600")
root.configure(background="black")

m = tk.Menu(root, tearoff=0, relief="flat", borderwidth=0, background="black", foreground="white")
f_menu = tk.Menu(m, tearoff=0, relief="flat", borderwidth=0, background="black", foreground="white")
f_menu.add_command(label="Open", background="black", foreground="white", hidemargin=True)
f_menu.add_command(label="Close", background="black", foreground="white", hidemargin=True)
f_menu.add_command(label="Merge", background="black", foreground="white", hidemargin=True)
f_menu.add_separator(background="white")
f_menu.add_command(label="Exit", command=root.destroy, background="black", foreground="white")

h_menu = tk.Menu(m, tearoff=0, relief="flat", borderwidth=0, background="black", foreground="white")
a_menu = tk.Menu(m, tearoff=0, relief="flat", borderwidth=0, background="black", foreground="white")

root.config(menu=m)

m.add_cascade(label="File", menu=f_menu)
m.add_cascade(label="Help", menu=h_menu)
m.add_cascade(label="About", menu=a_menu)

# Apply custom background to menus after they're created
root.update_idletasks()  # Ensure menu is created
root.update()  # Force a full update

# Force menu to be created by Windows
hwnd = root.winfo_id()
ctypes.windll.user32.DrawMenuBar(hwnd)

# Small delay to ensure menu is ready
root.after(100, lambda: set_menu_background(root, 0, (0, 0, 0)))  # File menu (position 0)
root.after(100, lambda: set_menu_background(root, 1, (0, 0, 0)))  # Help menu (position 1)
root.after(100, lambda: set_menu_background(root, 2, (0, 0, 0)))  # About menu (position 2)

root.mainloop()


# import tkinter as tk
# from tkinter import ttk
#
# Separator = object()
# Disabled = object()
#
#
# class FlatMenu(tk.Toplevel):
#     PADDING_XY = (10, 6)
#     CLOSE_DELAY_MS = 160
#
#     def __init__(self, master, items, *, parent_btn=None, root_owner=None):
#         super().__init__(master)
#         self.overrideredirect(True)
#         self.attributes("-topmost", True)
#         self.transient(master)
#
#         # Track the “stack” root so every submenu knows the top ancestor
#         self._stack_root = root_owner or self
#         self._parent_btn = parent_btn
#         self._open_child = None
#
#         self._frame = ttk.Frame(self, padding=0)
#         self._frame.pack(fill="both", expand=True)
#
#         style = ttk.Style(self)
#         style.configure("FlatMenu.TButton", anchor="w", padding=self.PADDING_XY)
#
#         self._build(items)
#
#         # Don’t auto-close on focus changes between menus
#         # self.bind("<FocusOut>", ...)  # ← removed
#
#         # Click-outside to close (unbind when destroyed)
#         self.bind_all("<ButtonPress-1>", self._on_global_click, add="+")
#         self.bind_all("<ButtonPress-3>", self._on_global_click, add="+")
#         self.bind("<Destroy>", lambda e: self._cleanup())
#
#         # Lightweight “hover watchdog” that closes when pointer leaves ALL menus
#         self._hover_job = None
#         self._schedule_hover_watch()
#
#     # ---- public -------------------------------------------------------------
#
#     def popup(self, x, y):
#         w, h = self._preferred_size()
#         x, y = self._clamp_to_screen(x, y, w, h)
#         self.geometry(f"{w}x{h}+{x}+{y}")
#         self.deiconify()
#
#     def close_all(self):
#         self._close_child()
#         # Only the stack root destroys the whole chain
#         if self is self._stack_root:
#             self.destroy()
#         else:
#             # Delegate to root
#             self._stack_root.close_all()
#
#     # ---- build --------------------------------------------------------------
#
#     def _build(self, items):
#         for spec in items:
#             if spec == (Separator,) or spec[0] is Separator:
#                 ttk.Separator(self._frame).pack(fill="x", padx=6, pady=4)
#                 continue
#
#             label = spec[0]
#             payload = spec[1] if len(spec) > 1 else None
#
#             if isinstance(payload, list):
#                 btn = ttk.Button(self._frame, text=f"{label}  ▸", style="FlatMenu.TButton")
#                 btn.pack(fill="x")
#                 # Open submenu on hover OR on click
#                 btn.bind("<Enter>", lambda e, p=payload, b=btn: self._open_submenu(b, p))
#                 btn.bind("<Button-1>", lambda e, p=payload, b=btn: self._open_submenu(b, p))
#                 # NOTE: we DO NOT close on <Leave> anymore
#                 continue
#
#             if payload is Disabled:
#                 ttk.Button(self._frame, text=label, style="FlatMenu.TButton", state="disabled").pack(fill="x")
#                 continue
#
#             ttk.Button(
#                 self._frame, text=label, style="FlatMenu.TButton",
#                 command=self._wrap_and_close(payload)).pack(fill="x")
#
#     # ---- behavior -----------------------------------------------------------
#
#     def _wrap_and_close(self, cmd):
#         def run():
#             self._stack_root.close_all()
#             if callable(cmd):
#                 cmd()
#
#         return run
#
#     def _open_submenu(self, btn, items):
#         # Close previous child (if any)
#         self._close_child()
#
#         child = FlatMenu(self, items, parent_btn=btn, root_owner=self._stack_root)
#         self._open_child = child
#
#         bx, by = btn.winfo_rootx(), btn.winfo_rooty()
#         bw, bh = btn.winfo_width(), btn.winfo_height()
#         cx, cy = bx + bw, by  # right side by default
#
#         w, h = child._preferred_size()
#         sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
#         if cx + w > sw:  # flip left if needed
#             cx = bx - w
#         cy = min(max(0, cy), sh - h)
#
#         child.popup(cx, cy)
#
#     def _close_child(self):
#         if self._open_child and self._open_child.winfo_exists():
#             # Child will unbind its own global events
#             self._open_child.destroy()
#         self._open_child = None
#
#     # ---- outside-click & hover watchdog ------------------------------------
#
#     def _on_global_click(self, event):
#         # Close only if click is outside ALL menus in the stack
#         if not self._pointer_over_any_menu():
#             self._stack_root.close_all()
#
#     def _schedule_hover_watch(self):
#         # Periodically check if pointer left all menus; if so, close (like native)
#         if self._hover_job:
#             self.after_cancel(self._hover_job)
#         self._hover_job = self.after(self.CLOSE_DELAY_MS, self._hover_tick)
#
#     def _hover_tick(self):
#         if not self._pointer_over_any_menu():
#             self._stack_root.close_all()
#             return
#         self._schedule_hover_watch()
#
#     def _pointer_over_any_menu(self):
#         px, py = self.winfo_pointerx(), self.winfo_pointery()
#         # Walk down the chain: self -> child -> grandchild...
#         w = self._stack_root
#         while w:
#             if w._under_pointer(w, px, py):
#                 return True
#             w = getattr(w, "_open_child", None)
#         return False
#
#     # ---- sizing/geometry helpers -------------------------------------------
#
#     def _preferred_size(self):
#         self.update_idletasks()
#         return self._frame.winfo_reqwidth(), self._frame.winfo_reqheight()
#
#     def _clamp_to_screen(self, x, y, w, h):
#         sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
#         return max(0, min(x, sw - w)), max(0, min(y, sh - h))
#
#     @staticmethod
#     def _under_pointer(widget, px, py):
#         wx, wy = widget.winfo_rootx(), widget.winfo_rooty()
#         return wx <= px < wx + widget.winfo_width() and wy <= py < wy + widget.winfo_height()
#
#     # ---- cleanup ------------------------------------------------------------
#
#     def _cleanup(self):
#         # Remove global binds when any menu in the stack dies
#         try:
#             self.unbind_all("<ButtonPress-1>")
#             self.unbind_all("<ButtonPress-3>")
#         except Exception:
#             pass
#
#
# # --- demo --------------------------------------------------------------------
# if __name__ == "__main__":
#     root = tk.Tk()
#     root.geometry("420x260")
#
#     def say(t): print(t)
#
#     cascaded = [
#         ("Open", lambda: say("Open")),
#         ("Close", lambda: say("Close")),
#         (Separator,),
#         ("Export", [
#             ("PNG", lambda: say("Export PNG")),
#             ("PDF", lambda: say("Export PDF")),
#             ("Advanced…", [
#                 ("High Quality", lambda: say("HQ")),
#                 ("Low Quality", lambda: say("LQ")),
#                 (Separator,),
#                 ("Disabled here", Disabled),
#             ]),
#         ]),
#         ("Disabled item", Disabled),
#         (Separator,),
#         ("Exit", root.destroy),
#     ]
#
#     def show_menu(event=None):
#         m = FlatMenu(root, cascaded)
#         x, y = root.winfo_pointerx(), root.winfo_pointery()
#         m.popup(x, y)
#
#     btn = ttk.Button(root, text="Right-click me for cascades")
#     btn.pack(padx=40, pady=40)
#     btn.bind("<Button-3>", show_menu)
#     btn.bind("<Button-1>", show_menu)  # demo
#
#     root.mainloop()