from ttkbootstrap import App
from ttkbootstrap.widgets import Button, Label
from ttkbootstrap.layouts.gridbox import GridBox  # alias of GridFrame

JUSTIFIES = ["start", "center", "end", "stretch"]   # horizontal
ALIGNS    = ["start", "center", "stretch"]          # vertical (plus 'end' below)

with App("GridBox — justify/align matrix", theme="dark") as app:
    app.geometry("900x520")

    # 3 rows × 4 columns, rows/cols are weighted so you can see alignment within cells
    with GridBox(
        columns=[1, 1, 1, 1],
        rows=[1, 1, 1],
        gap=16,
        padding=16,
        surface="background-1",
        sticky="nsew",
        expand=True,
        margin=16,
    ):
        # Row labels (left) + column labels (top)
        # Using auto-layout: 4 per row → 3 rows (12 buttons)

        # Row 1: align_self="start"
        for j in JUSTIFIES:
            Button(
                text=f"J:{j}  A:start",
                justify_self=j,        # horizontal behavior for this cell
                align_self="start",    # vertical behavior for this row
                padding=8,
            )

        # Row 2: align_self="center"
        for j in JUSTIFIES:
            Button(
                text=f"J:{j}  A:center",
                justify_self=j,
                align_self="center",
                padding=8,
            )

        # Row 3: align_self="stretch"
        for j in JUSTIFIES:
            Button(
                text=f"J:{j}  A:stretch",
                justify_self=j,
                align_self="stretch",
                padding=8,
            )

app.run()
