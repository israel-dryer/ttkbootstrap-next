import tkinter as tk


class MockDataSource:
    """Simulates a paged data source."""

    def __init__(self, items: list[dict]):
        self._data = items

    def total_count(self):
        return len(self._data)

    def read_record_by_index(self, index: int):
        return self._data[index]


class RowItem(tk.Frame):
    """Reusable composite row widget."""

    def __init__(self, parent, height=28):
        super().__init__(parent, height=height)
        self.label = tk.Label(self, anchor="w", padx=8)
        self.label.pack(fill="both", expand=True)
        self._record = {}

        self.bind("<Button-1>", self._on_click)
        self.label.bind("<Button-1>", self._on_click)

    def update(self, record: dict):
        self._record = record
        self.label.config(text=record["name"])
        bg = "#e0e0ff" if record.get("selected") else "white"
        self.config(bg=bg)
        self.label.config(bg=bg)

    def _on_click(self, event):
        self._record["selected"] = not self._record.get("selected", False)
        self.update(self._record)


class VirtualListBox(tk.Frame):
    def __init__(self, parent, items: list[dict], row_height=28, buffer=5):
        super().__init__(parent)

        self.row_height = row_height
        self.buffer = buffer
        self.datasource = MockDataSource(items)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.visible_rows = 0
        self.rows = []

        self.canvas.bind("<Configure>", self._on_resize)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.configure(scrollregion=(0, 0, 0, len(items) * row_height))
        self.after_idle(self._redraw)

    def _on_resize(self, event):
        needed = event.height // self.row_height + self.buffer
        if needed != self.visible_rows:
            self._init_rows(needed)
        self._redraw()

    def _init_rows(self, count):
        for rid in self.rows:
            self.canvas.delete(rid[1])
        self.rows.clear()

        for _ in range(count):
            widget = RowItem(self.canvas, height=self.row_height)
            wid = self.canvas.create_window(0, 0, anchor="nw", window=widget, width=self.canvas.winfo_width())
            self.rows.append((widget, wid))
        self.visible_rows = count

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._redraw()

    def _redraw(self):
        first = int(self.canvas.canvasy(0) // self.row_height)
        total = self.datasource.total_count()

        for i, (widget, wid) in enumerate(self.rows):
            index = first + i
            if 0 <= index < total:
                record = self.datasource.read_record_by_index(index)
                widget.update(record)
                y = index * self.row_height
                self.canvas.coords(wid, 0, y)
                self.canvas.itemconfigure(wid, state="normal")
            else:
                self.canvas.itemconfigure(wid, state="hidden")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Virtual ListBox")

    data = [{"id": i, "name": f"Item {i}", "selected": False} for i in range(1, 10001)]
    vlist = VirtualListBox(root, data)
    vlist.pack(fill="both", expand=True)

    root.geometry("400x600")
    root.mainloop()
