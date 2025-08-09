from typing import Literal, Union

BindScope = Literal['all', 'class', 'widget']
TraceOperation = Literal["array", "read", "write", "unset"]
VariableType = Union["Signal", "Variable", str]
WidgetType = Union["BaseWidget", "App", "Misc"]
