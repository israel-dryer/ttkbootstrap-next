#
#
# import tkinter as tk
#
#
# class FormEntry(tk.Frame):
#
#     def __init__(self, parent, label: str = "", message: str = "", value: str="", **kwargs):
#         super().__init__(parent, **kwargs)
#
#         self._label = tk.Label(self, text=label, anchor='w', font="TkCaptionFont")
#         self._field = tk.Frame(self)
#         self._message = tk.Label(self, anchor='w', text=message, font="TkCaptionFont")
#         self._prefix = []
#         self._postfix = []
#         self._entry = tk.Entry(self._field, font="TkDefaultFont")
#         self._entry.insert('end', value)
#         self._entry.pack(side='left', fill='both', expand=True)
#
#         self._field.pack(fill='x', expand=True)
#
#         if label:
#             self._label.pack(fill='x', before=self._field)
#
#         if message:
#             self._message.pack(fill='x', after=self._field)
#
#     def add_prefix(self, widget, **kwargs):
#         instance = widget(self._field, **kwargs)
#         self._prefix.append(instance)
#         instance.pack(side='left', before=self._entry)
#
#     def add_postfix(self, widget, **kwargs):
#         instance = widget(self._field, **kwargs)
#         self._postfix.append(instance)
#         instance.pack(side="left", after=self._entry)
#
#
# app = tk.Tk()
#
# fe = FormEntry(app, "Date")
# fe.add_postfix(tk.Button, text="📆", padx=2, pady=2)
# fe.pack(padx=16, pady=16, fill='x')
#
# f2 = FormEntry(app, "First Name", "Must be 8-20 characters long")
# f2.add_prefix(tk.Button, text="➕")
# f2.add_postfix(tk.Button, text="➖")
# f2.pack(padx=16, pady=16, fill='x')
#
# choose = FormEntry(app, value="No File Chosen")
# choose.add_prefix(tk.Button, text="Choose File")
# choose.pack(padx=16, pady=16, fill='x')
#
# username = FormEntry(app, value="Username")
# username.add_prefix(tk.Label, text="@")
# username.pack(padx=16, pady=16, fill='x')
#
# user2 = FormEntry(app, value="Recipient's username")
# user2.add_postfix(tk.Label, text="@example.com")
# user2.pack(padx=16, pady=16, fill='x')
#
# amounts = FormEntry(app)
# amounts.add_prefix(tk.Label, text='$')
# amounts.add_prefix(tk.Label, text='0.00')
# amounts.pack(fill='x', padx=16, pady=16)
#
# app.mainloop()

import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry('500x500')
style = ttk.Style()
style.theme_use('clam')

frame = ttk.Frame(root, padding=16)
frame.pack(fill='both', expand=True)

img = tk.PhotoImage(file='D:/Development/ttkbootstrap/src/ttkbootstrap/assets/widgets/input-md.png')

style.layout('TSpinbox',
                   [('Spinbox.field', {'side': 'top', 'sticky': 'we', 'children': [
    ('Spinbox.uparrow', {'side': 'left', 'sticky': 'ns'}),
    ('Spinbox.padding', {'side': 'left', 'sticky': 'nswe', 'children': [
        ('Spinbox.textarea', {'sticky': 'nswe'})
    ]}),
    ('Spinbox.downarrow', {'side': 'left', 'sticky': 'ns'})
]})])


# style.element_create('My.Entry.field', "image", img, sticky='nsew', padding=16, border=16)
#style.layout('My.Frame.border')

# style.layout('My.TEntry',
#                    [('My.Entry.field', {'sticky': 'nswe', 'border': '16', 'children': [('Entry.padding', {'sticky': 'nswe', 'children': [('Entry.textarea', {'sticky': 'nswe'})]})]})])

ttk.Spinbox(frame, style='TSpinbox', from_=0, to=100, increment=1).pack()

root.mainloop()