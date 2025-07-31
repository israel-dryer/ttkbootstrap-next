import tkinter as tk
from tkinter import ttk
from typing import Literal, Optional

"""
    Justify
        Start: side='left' (container: fill='x')
        Center: side='left' (container: None)
        End: side='right' (container: fill='x')... start from reversed list ?
        Space-Around: side='left', expand=True (container: fill='x')
        Space-Between: side='left', anchor=[first='w', last='e', other: 'center'] (container, fill='x')... not perfect but good enough
    Align
        start: anchor = 'n' + anchor
        end: anchor = 's' + anchor
        center: (default)
    Expand
        True
        False
    Fill:
        x, y, both    
"""


class StackFrame(ttk.Frame):

    def __init__(
            self,
            parent=None,
            gap: int = 0,
            orient: Literal['horizontal', 'vertical'] = 'horizontal',
            justify: Literal['start', 'center', 'end', 'space-between', 'space-around']='start',
            align: Literal['start', 'center', 'end'] = 'center',
            expand: bool = False,
            fill: Optional[Literal['x', 'y', 'both']] = None,
            **kwargs
    ):
        self._orient = orient
        self._gap = gap
        self._justify = justify
        self._align = align
        self._expand = expand
        self._fill = fill
        self._fit_content = kwargs.pop('fit_content', True)

        super().__init__(parent, **kwargs)

        # pack propagation
        if not self._fit_content:
            self.pack_propagate(False)


    def add_child(self, *widget, **kwargs):
        for child in widget:
            options = self._horizontal_options(child)
            options.update(**kwargs)
            child.pack(**options)

    def _horizontal_options(self, widget):
        options = dict()
        is_last_widget = self.winfo_children()[-1] == widget and len(self.winfo_children()) > 1

        # justify start
        if self._justify == 'start':
            options.update(side='left')
            if self._align == 'start':
                options.update(anchor='nw')
            elif self._align == 'end':
                options.update(anchor='sw')
            else:
                options.update(anchor='w')

        # justify end
        elif self._justify == 'end':
            options.update(side='right')
            if self._align == 'start':
                options.update(anchor='ne')
            elif self._align == 'end':
                options.update(anchor='se')
            else:
                options.update(anchor='e')

        # justify space-around
        elif self._justify == 'space-around':
            options.update(side='left', expand=True)
            if self._align == 'start':
                options.update(anchor='w')
            elif self._align == 'end':
                options.update(anchor='e')


        # justify space-between
        elif self._justify == 'space-between':

            def space_between_anchor(index, count, align):
                if index == 0:
                    if align == 'start':
                        return 'nw'
                    elif align == 'end':
                        return 'sw'
                    else:
                        return 'w'
                elif index == count - 1:
                    if align == 'start':
                        return 'ne'
                    elif align == 'end':
                        return 'se'
                    else:
                        return 'e'
                else:
                    if align == 'start':
                        return 'w'
                    elif align == 'end':
                        return 'e'
                    else:
                        return 'center'

            # these options need to be recalculated for each child widget
            for i, child in enumerate(self.pack_slaves()):
                anchor = space_between_anchor(i, len(self.pack_slaves()), self._align)
                if i == 0:
                    child.pack(side='left', anchor=anchor, padx=(0, self._gap), expand=True)
                elif i == len(vstack.pack_slaves()):
                    child.pack(side='left', anchor=anchor, expand=True)
                else:
                    child.pack(side='left', anchor=anchor, padx=(0, self._gap), expand=True)

        # other options
        options.setdefault('fill', self._fill)
        options.setdefault('expand', self._expand)
        return options

    def remove_child(self, *widget):
        for child in widget:
            child.pack_forget()
        return self

    def add_child_after(self, *widget, after, **kwargs):
        for child in widget:
            options = self._horizontal_options(child)
            options.update(**kwargs)
            child.pack(after=after, **options)
        return self

    def configure_child(self, widget, option=None, **kwargs):
        if option is None:
            widget.pack(**kwargs)
            return self
        else:
            return widget.pack(option)


root = tk.Tk()
root.geometry('400x400')
root.configure(background='yellow')

# vstack = StackFrame(root, padding=8, gap=8, justify='space-between')
# vstack.pack(fill='both')

vstack = StackFrame(root, justify='space-between')
vstack.pack(fill='both')

for x in range(4):
    vstack.add_child(tk.Button(vstack, text='Button'))

# for i, w in enumerate(vstack.pack_slaves()):
#     if i == 0:
#         w.pack(side='left', anchor='w')
#     elif i == len(vstack.pack_slaves()) - 1:
#         w.pack(side='right', anchor='e')
#     else:
#         w.pack(side='left', anchor='center')


# hstack = StackFrame(root, padding=8, gap=8, orient='vertical')
# hstack.pack(fill='both')
#
# for d in range(4):
#     hstack.add_child(tk.Button(hstack, text='Button'), expand=True)

# frame = tk.Frame(root, height=30)
# frame.pack(fill='x', side='top')
# frame.pack_propagate(False)  # fit_content = `False`
#
# for x in range(5):
#     if x == 0:
#         anchor='nw'
#         expand = 1
#     elif x == 4:
#         anchor='ne'
#         expand = 1
#     else:
#         anchor='n'
#         expand = 1
#     ttk.Button(frame, text='Button').pack(side='left')

root.mainloop()