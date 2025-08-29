from ttkbootstrap.app import App
from ttkbootstrap.layouts import Grid
from ttkbootstrap.layouts.pack import Pack
from ttkbootstrap.widgets.label import Label
from ttkbootstrap.widgets.button import Button
from ttkbootstrap.routing import Router, Route, RouterOutlet, navigate

# TODO understand the routing & simplify
# TODO replace lifecycle handlers and calls with the emit/bind pattern
# TODO standardize view creation with an @view class decorator that sets the title, router, and other metadata
# TODO what's the point of registering a global router? can I have multiple routers?
# TODO possibly generate other calls like on-navigated, etc...

class HomeView(Pack):
    def __init__(self):
        super().__init__(surface="green-100", direction="vertical", gap=8, padding=16)
        with self:
            Label(text="Home (no layout specified in route)")
            Button(text="Go to /user/42").on_click(lambda: navigate("/user/42"))

    def on_mount(self, params=None):
        # After outlet applies its default, this will be 'pack'
        print("HomeView manager:", self.widget.winfo_manager())

class UserView(Pack):
    def __init__(self, id=None):
        super().__init__(surface="red-100", direction="vertical", gap=8, padding=16)
        with self:
            Label(text=f"User: {id} (route lays out with fill='x')")
            Button(text="Back").on_click(lambda: navigate("/"))

    def on_mount(self, params=None):
        print("UserView manager:", self.widget.winfo_manager())

class SidebarView(Pack):
    def __init__(self):
        super().__init__(surface="gray-400", direction="vertical", gap=8, padding=16)
        for x in range(5):
            Button(f"Button {x}")

app = App(title="Router Default Layout Demo")

routes = [
    # No .layout() here -> outlet will apply default: fill="both", expand=True
    Route(path="/", view=lambda: HomeView()),

    # Explicit layout in the route -> outlet respects this and does NOT override
    Route(path="/user/:id", view=lambda id=None: UserView(id=id).layout(fill="x")),

    Route(path="/sidebar", view=SidebarView),
]

router = Router(routes)

with app:
    with Grid(rows=[0, 1], columns=[0, 1]).layout(fill="both", expand=True):
        Label(text="This is the toolbar", background="blue-200").layout(columnspan=2, sticky="ew")
        RouterOutlet().layout(row=1, column=1, sticky="nsew")
        RouterOutlet(name="extra").layout(row=1, column=0, sticky="n")

router.navigate("/")     # HomeView will fill the outlet by default
router.navigate("sidebar", outlet="extra")
app.run()
