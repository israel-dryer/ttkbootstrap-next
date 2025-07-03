# Layout Management

Currently in Tkinter, layout is specified by the child using the pack, place, grid managers.

One of the challenges is that each component must specify a parent upon initialization, however, that does not mean that
a parent widget cannot pack it's own children.

I'm thinking of a `StackFrame` and a `GridFrame` that allows for easier layout management. The idea is that the
StackFrame will allow for things such as `gap`, `alignment`, `justification`, etc. The child can add to these updates by
specifying layout properties in it's own constructor.

The question becomes whether I keep the traditional layout managers or whether I abstract that away.

I can think about that later, but the layout attributes can be injected via a mixin when I'm ready to implement.

