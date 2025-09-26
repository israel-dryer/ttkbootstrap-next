from ttkbootstrap import App, Button, Frame, Grid


def greet():
    print("Hello world")


app = App(title="Demo Legacy Layout", geometry="200x200")

g = Frame(parent=app)
g.widget.pack(fill='both', expand=True)
g.widget.grid_columnconfigure(0, weight=1)
g.widget.grid_rowconfigure(0, weight=1)
g.widget.grid_rowconfigure(1, weight=1)

Button(parent=g, text="Push", icon="house-fill", command=greet).widget.grid(sticky="nsew")
Button(parent=g, text="Button", color="danger", variant="outline").widget.grid(sticky="nsew")

app.run()

# with App(title="Demo Legacy Layout", geometry="200x200") as app:
#     with Grid(rows=[1, 1], columns=[1], sticky_items="nsew").layout(fill='both', expand=True):
#         Button(text="Push", icon="house-fill", command=greet)
#         Button(text="Button", color="danger", variant="outline")
# app.run()
