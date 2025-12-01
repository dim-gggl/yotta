# yotta
Build beautiful CLIs and TUIs in Python, the Django way.

yotta is a modern framework designed to simplify the creation of Command Line Interfaces (CLI) and Terminal User Interfaces (TUI).

It combines the robustness of Click, the beauty of Rich, and the interactivity of Textual within a modular architecture inspired by Django.

## Why yotta?

Developing complex CLIs often ends up in "spaghetti code." yotta brings structure to the chaos:
- Modular Architecture: Split your code into reusable "Apps" (startproject, startapp).
- UI-First: A native UX engine. Display tables, spinners, and alerts without manually importing Rich.
- Hybrid TUI Mode: Transform a command into a full interactive dashboard (mouse/keyboard) via native Textual integration.
- Smart Arguments: Automatic validation (Email, Files, Ranges) before your code even runs.

## Installation

For now (local development):
```bash
git clone [https://github.com/dim-gggl/yotta.git](https://github.com/dim-gggl/yotta.git)
cd yotta
pip install -e .
```
## Quick Start

1. Create a new project

yotta scaffolds the entire folder structure for you.
```bash
yotta startproject my_cli
cd my_cli
```
2. Create an app (module)
```bash
python manage.py startapp inventory
```
> Note: Don't forget to add 'src.inventory' to INSTALLED_APPS in your yotta_settings.py file.
3. Write your first command
In src/inventory/commands.py:
```python
from yotta.cli.decorators import command, argument
from yotta.core.context import Context
from yotta.cli.types import EMAIL

@command(name="add_user", help="Adds a user to the inventory")
@argument("email", type=EMAIL)
def add_user(ctx: Context, email: str):
    # Using the native UI engine
    ctx.ui.header("New User")
    
    with ctx.ui.spinner("Checking database..."):
        # Simulate work
        import time; time.sleep(1)
        
    ctx.ui.success(f"User [bold]{email}[/] added successfully!")
    
    # Automatic formatted table
    ctx.ui.table(
        columns=["ID", "Email", "Status"],
        rows=[["1", email, "Active"]],
        title="Summary"
    )

```
4. Run the command
```bash
python manage.py add_user contact@example.com
```

## TUI Mode (Textual Integration)
Need a real-time interactive dashboard? yotta integrates Textual natively.

Define a view in src/inventory/ui.py:
```python
from yotta.ui.tui import yottaApp
from textual.widgets import Placeholder

class MonitorDashboard(yottaApp):
    def compose(self):
        yield Placeholder("Performance charts here")

```
Launch it from a standard command:
```python
@command(name="monitor")
def launch_monitor(ctx: Context):
    app = MonitorDashboard(title="Super Monitor")
    app.run()

```
## Key Features
### The UI Context (ctx.ui)

yotta injects a ui wrapper into all your commands. No need to instantiate Console everywhere.

|Method|Description|
|:--|:--|
|`ctx.ui.header(title, subtitle)`|Displays a stylized panel header.|
|`ctx.ui.success(msg)`|Displays a success message (green).|
|`ctx.ui.error(msg)`|Displays an error message (red).|
|`ctx.ui.table(cols, rows)`|Generates a formatted Rich table.|
|`ctx.ui.spinner(msg)`|Context manager for an animated loader.|
|`ctx.ui.confirm(question)`|Interactive Yes/No prompt.|

### Smart Types (yotta.cli.types)

Validate user input without writing a single if/else.

`EMAIL`: Validates email format (Regex).

`File(extension='.json')`: Checks for file existence AND specific extension.

`Range(min=18, max=99)`: Enforces numeric range.

## Project Structure
```
my_cli/
├── manage.py            # Entry point (Django-like)
├── yotta_settings.py     # Global configuration
└── src/                 # Your applications folder
    ├── main/
    │   ├── commands.py  # Your CLI commands
    │   └── ui.py        # Your visual components
    └── inventory/
        ├── commands.py
        └── ...
```