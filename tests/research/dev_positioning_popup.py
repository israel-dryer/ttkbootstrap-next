import tkinter as tk
from tkinter import ttk
from typing import Callable, Literal

Anchor = Literal["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"]


class Popup(tk.Toplevel):
    def __init__(
        self,
        parent,
        content_factory: Callable[[tk.Widget], tk.Widget],
        *,
        relative_to=None,
        anchor: Anchor = "s",
        x=None,
        y=None,
        center=False,
        follow=False,
        padding=10,
        autohide=True,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.withdraw()
        self.overrideredirect(True)
        self.transient(parent)

        self._parent = parent
        self._relative_to = relative_to
        self._anchor = anchor
        self._x = x
        self._y = y
        self._center = center
        self._follow = follow

        frame = ttk.Frame(self, padding=padding, relief="solid", borderwidth=1)
        frame.pack(expand=True, fill="both")
        self.content = content_factory(frame)
        self.content.pack(expand=True, fill="both")

        self.after(1, self._position)

        if autohide:
            self.bind("<FocusOut>", lambda e: self.hide())
            self.bind("<Escape>", lambda e: self.hide())
            self.content.bind("<Button-1>", lambda e: e.widget.focus_set())

        if follow and relative_to:
            self._bind_follow(relative_to)

    def _position(self):
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()

        if self._center:
            x = self.winfo_screenwidth() // 2 - width // 2
            y = self.winfo_screenheight() // 2 - height // 2
        elif self._relative_to:
            rx = self._relative_to.winfo_rootx()
            ry = self._relative_to.winfo_rooty()
            rw = self._relative_to.winfo_width()
            rh = self._relative_to.winfo_height()

            match self._anchor:
                case "n":
                    x = rx + rw // 2 - width // 2
                    y = ry - height
                case "ne":
                    x = rx + rw
                    y = ry - height
                case "e":
                    x = rx + rw
                    y = ry + rh // 2 - height // 2
                case "se":
                    x = rx + rw
                    y = ry + rh
                case "s":
                    x = rx + rw // 2 - width // 2
                    y = ry + rh
                case "sw":
                    x = rx - width
                    y = ry + rh
                case "w":
                    x = rx - width
                    y = ry + rh // 2 - height // 2
                case "nw":
                    x = rx - width
                    y = ry - height
                case "center":
                    x = rx + rw // 2 - width // 2
                    y = ry + rh // 2 - height // 2
                case _:
                    x = rx
                    y = ry + rh
        elif self._x is not None and self._y is not None:
            x = self._x
            y = self._y
        else:
            x = 100
            y = 100

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.deiconify()
        self.focus_force()

    def _bind_follow(self, widget):
        def on_configure(event):
            self._position()
        widget.bind("<Configure>", on_configure, add=True)
        self._parent.bind("<Configure>", on_configure, add=True)

    def hide(self):
        self.withdraw()
        self.after(100, self.destroy)


# ------------------------------------
# DEMO USAGE
# ------------------------------------
def main():
    root = tk.Tk()
    root.geometry("500x400")
    root.title("Popup Anchor Demo")

    # Helper to create popup launcher
    def make_popup(anchor: Anchor):
        def open_popup():
            Popup(
                root,
                lambda parent: ttk.Label(parent, text=f"Anchor: {anchor.upper()}"),
                relative_to=btn,
                anchor=anchor,
                follow=True
            )
        return open_popup

    ttk.Label(root, text="Click a button to open a popup anchored to that side:").pack(pady=(20, 10))

    # Central button to anchor to
    btn = ttk.Button(root, text="Anchor Target")
    btn.place(relx=0.5, rely=0.5, anchor="center")

    # Buttons for all 8 directions + center
    anchors = ["n", "ne", "e", "se", "s", "sw", "w", "nw", "center"]
    buttons = []
    for anchor in anchors:
        b = ttk.Button(root, text=anchor.upper(), command=make_popup(anchor))
        buttons.append(b)

    # Arrange control buttons in a grid
    grid = [
        [buttons[7], buttons[0], buttons[1]],  # NW, N, NE
        [buttons[6], buttons[8], buttons[2]],  # W, Center, E
        [buttons[5], buttons[4], buttons[3]]   # SW, S, SE
    ]
    for r, row in enumerate(grid):
        for c, b in enumerate(row):
            b.place(x=50 + c * 120, y=300 + r * 40)

    root.mainloop()


if __name__ == "__main__":
    main()
