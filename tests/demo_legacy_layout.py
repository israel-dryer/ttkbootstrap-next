from ttkbootstrap import App, Button, Frame, Grid


def greet():
    print("Hello world")


app = App(title="Demo Legacy Layout", geometry="200x200")

g = Grid(parent=app, rows=[1, 1], columns=[1], sticky_items="nsew").attach(fill="both", expand=True)
Button(parent=g, text="Push", icon="house-fill", command=greet).attach()
Button(parent=g, text="Button", color="danger", variant="outline").attach()

app.run()
