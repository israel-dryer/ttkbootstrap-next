from ttkbootstrap import App, Pack, Label
from ttkbootstrap.style import Typography
#
# with App("Typography Demo") as app:
#     with Pack(padding=16, gap=16, direction="column").attach():
#         for token in Typography.all()._fields:
#             Label(text=token.replace("_", " ").title(), font=token.replace('_', '-')).attach()
#
# app.run()


with App("Typography Demo") as app:
    for token in Typography.all()._fields:
        Label(text=token.replace("_", " ").title(), font=token.replace('_', '-')).attach()

app.run()
