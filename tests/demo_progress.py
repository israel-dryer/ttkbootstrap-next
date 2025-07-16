from ttkbootstrap.core import App
from ttkbootstrap.widgets import ProgressBar

app = App(title="Demo Progress")

ProgressBar(app, value=75, color="primary").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="secondary").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="success").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="warning").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="danger").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="light").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="dark").pack(fill='x', padx=16, pady=16)

ProgressBar(app, value=75, color="primary", variant="striped").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="secondary", variant="striped").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="success", variant="striped").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="warning", variant="striped").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="danger", variant="striped").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="light", variant="striped").pack(fill='x', padx=16, pady=16)
ProgressBar(app, value=75, color="dark", variant="striped").pack(fill='x', padx=16, pady=16)

ProgressBar(app, value=75, orient="vertical", color="primary").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="secondary").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="success").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="warning").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="danger").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="light").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="dark").pack(fill='y', expand=True, side='left', padx=16, pady=16)

ProgressBar(app, value=75, orient="vertical", color="primary", variant="striped").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="secondary", variant="striped").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="success", variant="striped").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="warning", variant="striped").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="danger", variant="striped").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="light", variant="striped").pack(fill='y', expand=True, side='left', padx=16, pady=16)
ProgressBar(app, value=75, orient="vertical", color="dark", variant="striped").pack(fill='y', expand=True, side='left', padx=16, pady=16)


app.run()