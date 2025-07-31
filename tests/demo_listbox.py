import tkinter as tk
from ttkbootstrap.core.datasource import DataSource


class ListRow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, height=28)
        self.label = tk.Label(self, anchor="w", padx=8)
        self.label.pack(fill="both", expand=True)

    def update(self, record: dict):
        if not record:
            self.label.config(text="", bg=self["bg"])
            return

        name = record.get("name", "Unnamed")
        selected = record.get("selected", False)
        bg = "#e0f7fa" if selected else "#ffffff"

        self.label.config(text=name, bg=bg)
        self.config(bg=bg)


class VirtualListBox(tk.Frame):
    def __init__(self, parent, items: list[dict], page_size=25, row_height=28, row_factory=None):
        super().__init__(parent)

        self._datasource = DataSource(page_size=page_size)
        self._datasource.set_data(items)

        self.row_height = row_height
        self.buffer_rows = 5
        self.visible_rows = 0
        self.row_widgets = []
        self.row_ids = []
        self.first_visible_index = 0
        self.row_factory = row_factory or self._default_row_factory

        # Search bar
        self.search_entry = tk.Entry(self)
        self.search_entry.pack(fill="x", padx=4, pady=4)
        self.search_entry.bind("<Return>", self._on_search)

        # Navigation
        nav = tk.Frame(self)
        nav.pack(fill="x", padx=4, pady=4)
        tk.Button(nav, text="Sort by Name", command=lambda: self.sort_items("name")).pack(side="left")
        tk.Button(nav, text="Clear Search", command=self.clear_search).pack(side="left")

        # Scrollable Canvas
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self._on_scroll)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.inner = tk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self._enable_mousewheel()
        self._init_rows()
        self.after(10, self._update_scroll_region)
        self.after(20, self._redraw)

    def _default_row_factory(self, parent):
        frame = tk.Frame(parent, height=self.row_height)
        label = tk.Label(frame, anchor="w", padx=8)
        label.pack(fill="both", expand=True)

        def update(record: dict):
            name = record.get("name", "Unnamed")
            selected = record.get("selected", False)
            bg = "#f0f0f0" if selected else "#ffffff"
            frame.config(bg=bg)
            label.config(text=name, bg=bg)

        frame.update = update
        return frame

    def _enable_mousewheel(self):
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            self._redraw()

        def bind_mousewheel(widget):
            widget.bind("<Enter>", lambda e: widget.bind_all("<MouseWheel>", _on_mousewheel))
            widget.bind("<Leave>", lambda e: widget.unbind_all("<MouseWheel>"))

        bind_mousewheel(self.canvas)
        bind_mousewheel(self.inner)
        self._bind_rows_mousewheel = bind_mousewheel

    def _on_canvas_resize(self, event):
        height = self.canvas.winfo_height()
        new_visible = height // self.row_height + self.buffer_rows
        if new_visible != self.visible_rows:
            self.visible_rows = new_visible
            self._init_rows()
            self._redraw()

    def _init_rows(self):
        for rid in self.row_ids:
            self.canvas.delete(rid)
        self.row_widgets.clear()
        self.row_ids.clear()

        self.visible_rows = self.visible_rows or (self.canvas.winfo_height() // self.row_height + self.buffer_rows)

        for i in range(self.visible_rows):
            row = self.row_factory(self.canvas)
            if hasattr(self, "_bind_rows_mousewheel"):
                self._bind_rows_mousewheel(row)
            row_id = self.canvas.create_window(0, i * self.row_height, anchor="nw", window=row)
            self.row_widgets.append(row)
            self.row_ids.append(row_id)

    def _update_scroll_region(self, event=None):
        total = self._datasource.total_count()
        content_height = total * self.row_height
        self.canvas.configure(scrollregion=(0, 0, self.canvas.winfo_width(), content_height))

    def _on_scroll(self, first, last):
        self.scrollbar.set(first, last)
        self._redraw()

    def _redraw(self):
        if not self.row_widgets:
            return

        y_offset = self.canvas.canvasy(0)
        first_index = int(y_offset // self.row_height)
        total = self._datasource.total_count()
        self.first_visible_index = max(0, min(first_index, total - self.visible_rows))

        for i, row in enumerate(self.row_widgets):
            record_index = self.first_visible_index + i
            if record_index >= total:
                row.update({})
                self.canvas.itemconfig(self.row_ids[i], state="hidden")
                continue

            page = self._datasource.get_page(page=record_index // self._datasource.page_size)
            record = page[record_index % self._datasource.page_size]

            def make_click(id_):
                return lambda e: self._toggle_selection(id_)

            row.update(record)
            row.bind("<Button-1>", make_click(record["id"]))
            self.canvas.coords(self.row_ids[i], 0, record_index * self.row_height)
            self.canvas.itemconfig(self.row_ids[i], width=self.canvas.winfo_width(), state="normal")

    def _toggle_selection(self, record_id):
        rec = self._datasource.read_record(record_id)
        if rec.get("selected"):
            self._datasource.unselect_record(record_id)
        else:
            self._datasource.select_record(record_id)
        self._redraw()

    def _on_search(self, event):
        self.search_items(self.search_entry.get())

    def search_items(self, term: str):
        if not term:
            self.clear_search()
            return
        self._datasource.set_filter(f"name LIKE '%{term}%'")
        self._update_scroll_region()
        self._redraw()

    def clear_search(self):
        self._datasource.set_filter("")
        self._update_scroll_region()
        self._redraw()


    def sort_items(self, by: str, descending=False):
        direction = "DESC" if descending else "ASC"
        self._datasource.set_sort(f"{by} {direction}")
        self._redraw()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Virtualized ListBox with Row Factory")

    data = [{"id": i, "name": f"Item {i}"} for i in range(1, 10001)]
    lb = VirtualListBox(root, data, page_size=100, row_factory=ListRow)
    lb.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()
