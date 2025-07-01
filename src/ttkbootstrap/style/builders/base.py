from ..element import Element, ElementImage
from ..style import Style
from ..theme import ColorTheme


class StyleBuilderBase:

    def __init__(self, target_style: str, surface: str = None, **options):
        self._target = target_style
        self._surface = surface or "base"
        self._theme = ColorTheme.instance()
        self._style = Style()
        self.options = options or dict()

    @property
    def theme(self):
        return self._theme

    def surface(self, value: str = None):
        """Get or set the surface type"""
        if value is None:
            return self._surface
        else:
            self._surface = value
            return self

    def resolve_name(self):
        """Return the resolved ttk style name"""
        return ".".join(
            [str(x) for x in self.options.values()] + [self.surface()] + [self.theme.name, self._target]
        )

    def exists(self):
        return self._style.style_exists(self.resolve_name())

    def build(self):
        """Build and return style name"""
        name = self.resolve_name()
        if not self.exists():
            self.register_style()
        return name

    def register_style(self):
        """Register the style (to be implemented by subclass"""
        raise NotImplemented("Must be implemented by subclass")

    def configure(self, style, **kwargs):
        self._style.configure(style, **kwargs)

    def map(self, style, **options):
        self._style.map(style, **options)

    def create_element(self, element: ElementImage):
        name, args, kwargs = element.build()
        self._style.create_element(name, "image", *args, **kwargs)

    def style_layout(self, ttk_style, element: Element):
        self._style.layout(ttk_style, [element.spec()])

    @property
    def style(self):
        return self._style
