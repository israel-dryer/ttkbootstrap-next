import enum


class EventEnum(enum.IntEnum):
    KeyPress = 2
    KeyRelease = 3
    ButtonPress = 4
    ButtonRelease = 5
    Motion = 6
    Enter = 7
    Leave = 8
    FocusIn = 9
    FocusOut = 10
    Keymap = 11
    Expose = 12
    GraphicsExpose = 13
    NoExpose = 14
    Visibility = 15
    Create = 16
    Destroy = 17
    Unmap = 18
    Map = 19
    MapRequest = 20
    Reparent = 21
    Configure = 22
    ConfigureRequest = 23
    Gravity = 24
    ResizeRequest = 25
    Circulate = 26
    CirculateRequest = 27
    Property = 28
    SelectionClear = 29
    SelectionRequest = 30
    Selection = 31
    Colormap = 32
    ClientMessage = 33
    Mapping = 34
    VirtualEvent = 35
    Activate = 36
    Deactivate = 37
    MouseWheel = 38

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, EventEnum):
            return self.value == other.value
        if isinstance(other, str):
            return self.name == other
        return NotImplemented


