# Layout Managers

Layouts in tkinter are a bit complicated. The parent is set explicitly in the child, and then the layout manager is
called on the child.

This library will add functions on the layout components themselves that will make this much more intuitive, as well as
provide additional functionality such as 'spacing' and 'alignment'

## Layouts

- StackFrame
- BoxFrame
- GridFrame
- FormFrame
- AbsoluteFrame

### StackFrame

**Properties**
- orient = 'horizontal'
- padding
- gap
- justify
- align
- fit_content

**Methods**
- add_child(*widget, **kwargs)
- add_child_after(*widget, after, **kwargs)
- remove_child(*widget)
- configure_child(widget, option=None, **kwargs)
