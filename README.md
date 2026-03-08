# <div align="center">yotta

<div align="center">
    <a href="https://www.python.org/">
      <img alt="Python Badge" src="https://img.shields.io/badge/python-3.10%2B-blue?style=plastic&logo=python&logoColor=yellow">
    </a>
    <a href="https://docs.astral.sh/uv/">
      <img alt="uv Badge" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json">
    </a>
    <a href="https://rich.readthedocs.io/en/stable/index.html">
      <img alt="Static Badge" src="https://img.shields.io/badge/rich-14.3.3%2B-%238b36db">
    </a>
    <a href="https://click.palletsprojects.com/en/stable/">
      <img alt="Static Badge" src="https://img.shields.io/badge/click-8.3.1%2B-%23cea3c7?style=plastic&logo=click&logoColor=%23cea3c7">
    </a>
    <a href="https://pypi.org/project/rich-click/">
      <img alt="Yes Yotta Badge" class="" src="https://img.shields.io/badge/rich--click-1.9.7%2B-%23800000?style=plastic&logo=rich-click&logoColor=%23800000">
    </a>
</div>

![](https://raw.githubusercontent.com/dim-gggl/yotta/main/media/yotta_dark.svg)

Build complete CLIs and TUIs in Python, the fast way. (Django-inspired)

yotta is designed to simplify the creation of Command Line Interfaces (CLI) and Terminal User Interfaces (TUI).

It combines the robustness of Click, the beauty of Rich, and the interactivity of Textual within a modular architecture inspired by Django.

## Why yotta?

Most CLI applications follow the same foundational patterns. yotta packages those patterns into a framework so you can ship faster without giving up structure, readability, or user experience.

Building a CLI app with yotta is making sure to get:
- Modular Architecture: Split your code into reusable "Apps" (startproject, startapp).
- UI-First Spirit: A native UX engine. Display tables, spinners, and alerts without manually importing Rich.
- Hybrid TUI Mode: Transform a command into a full interactive dashboard (mouse/keyboard) via native Textual integration.
- Smart Arguments: Automatic validation (Email, Files, Ranges) before your code even runs.

## Installation

### Install the CLI from PyPI

Use a global tool install if you want the `yotta` command available everywhere:

```bash
uv tool install yotta-framework
yotta --version
```

### Add yotta to a project

If you want to use yotta inside an existing project managed by `uv`:

```bash
uv add yotta-framework
```

### Development setup

If you want to work on yotta itself:

```bash
git clone https://github.com/dim-gggl/yotta.git
cd yotta
uv sync --all-extras
uv pip install -e .
```
## Quick Start

1. Create a new project

yotta scaffolds the entire folder structure for you.
```bash
yotta startproject my_cli
cd my_cli
uv sync
# A pyproject.toml and .env.example (with YOTTA_SETTINGS_MODULE) are created for you
```
2. Create an app (module)
```bash
uv run ./manage.py startapp inventory
```
> Note: Don't forget to add 'my_cli.inventory' (replace with your project name) to INSTALLED_APPS in your settings.py file.
3. Scaffold a command interactively (optional)
```bash
uv run ./manage.py startcommand
```
Follow the prompts to pick the target app, command name, arguments, and options. yotta will append a ready-to-edit function to the selected app's `commands.py`.
4. Write your first command
In `my_cli/inventory/commands.py`:
```python
import time

from yotta.cli.decorators import command, argument
from yotta.core.context import YottaContext
from yotta.core.types import EMAIL


@command(name="add_user", help="Adds a user to the inventory")
@argument("email", type=EMAIL)
def add_user(yotta: YottaContext, email: str) -> None:
    # Using the native UI engine
    yotta.ui.header("New User")
    # Access project configuration without extra imports
    # (settings are loaded lazily on first attribute access)
    _ = yotta.settings

    with yotta.ui.spinner("Checking database..."):
        # Simulate work
        time.sleep(1)

    yotta.ui.success(f"User [bold]{email}[/] added successfully!")

    # Automatic formatted table
    yotta.ui.table(
        columns=["ID", "Email", "Status"],
        rows=[["1", email, "Active"]],
        title="Summary",
    )
```
5. Run the command
```bash
uv run ./manage.py add_user contact@example.com
```

### Settings and environment
- `YOTTA_SETTINGS_MODULE` is loaded from `.env` or `.env.local` (the latter overrides).
- You can also set `YOTTA_ENV=prod` to auto-load `settings_prod.py`.
- `YOTTA_DEBUG=1` will surface full tracebacks during settings import and loader errors.
- `THEME` controls the console palette. Supported values: `"default"`, `"dark"` (unknown values fall back to `"default"`).

To override the theme, set it in your project's `settings.py`:

```python
# settings.py
THEME = "dark"
```

### Debugging imports and discovery
- Loader warnings surface when an app has no `commands.py`; use `--verbose` for extra details or `--quiet` to silence.
- Use `--strict` to fail fast on missing/broken command modules (useful in CI).

## TUI Mode (Textual Integration)
Need a real-time interactive dashboard? yotta integrates Textual natively.

Define a view in `my_cli/inventory/ui.py`:
```python
from textual.app import ComposeResult
from textual.widgets import Placeholder
from yotta.ui.tui import YottaApp


class MonitorDashboard(YottaApp):
    def compose(self) -> ComposeResult:
        yield Placeholder("Performance charts here")

```
Launch it from a standard command:
```python
from yotta.cli.decorators import command
from yotta.core.context import YottaContext


@command(name="monitor")
def launch_monitor(yotta: YottaContext) -> None:
    app = MonitorDashboard(title="Super Monitor")
    app.run()

```
## Key Features
### The UI Context (yotta.ui)

yotta injects a ui wrapper into all your commands. No need to instantiate Console everywhere.

|Method|Description|
|:--|:--|
|`yotta.ui.header(title, subtitle)`|Displays a stylized panel header.|
|`yotta.ui.success(msg)`|Displays a success message (green).|
|`yotta.ui.error(msg)`|Displays an error message (red).|
|`yotta.ui.table(cols, rows)`|Generates a formatted Rich table.|
|`yotta.ui.spinner(msg)`|Context manager for an animated loader.|
|`yotta.ui.confirm(question)`|Interactive Yes/No prompt.|

### RichUI - Unified Access to All Rich Components

Need direct access to Rich components? Use the `rich` singleton to instantiate any Rich component without manual imports.

```python
from yotta.ui import rich

# Instead of: from rich.align import Align
align = rich.align("Centered text", align="center")

# Instead of: from rich.syntax import Syntax
syntax = rich.syntax(code, "python", theme="monokai")

# Instead of: from rich.table import Table
table = rich.table(title="My Data")

# Instead of: from rich.tree import Tree
tree = rich.tree("Root")

# Instead of: from rich.panel import Panel
panel = rich.panel("Content", title="Info")
```

**Available components and utilities:**

- **Core:** console, group
- **Layout:** align, columns, constrain, layout, padding
- **Containers:** panel
- **Text & Styling:** color, emoji, pretty, style, styled, syntax, text, theme, markdown
- **Tables & Trees:** table, tree
- **Progress:** progress, spinner, status, live (with bar_column, text_column, etc.)
- **Prompts:** prompt, confirm, int_prompt, float_prompt
- **Rendering:** rule, segment, traceback, json
- **Utilities:** pprint, pretty_repr, install_traceback, escape_markup, render_markup

**Box styles:** Access via `rich.ROUNDED`, `rich.HEAVY`, `rich.DOUBLE`, `rich.MINIMAL`

This singleton approach provides seamless access to all Rich functionality through a single import, keeping your code clean and consistent.

### Smart Types (yotta.core.types)

Validate user input without writing a single if/else.

`EMAIL`: Validates email format (Regex).

`File(extension='.json')`: Checks for file existence AND specific extension.

`Range(min=18, max=99)`: Enforces numeric range.

`Choice([...])`: Restrict values to a predefined list (case-insensitive by default).

`Path() / Directory()`: Validate existing filesystem paths (files or directories).

`UUID()`: Validate UUID strings.

`URL()`: Validate http/https URLs.

`JSON()`: Accept JSON strings or paths to JSON files, returns parsed objects.

`Port(min,max)`: Validate port numbers in the allowed range.

`EnumChoice(MyEnum)`: Use Python Enums as a source of allowed values.

## Project Structure
```
my_cli/
├── .env.example           # Environment bootstrap
├── manage.py              # Project entry point
├── pyproject.toml         # Project metadata and dependencies
├── settings.py            # Global configuration
└── my_cli/                # Your applications folder (as a package)
    ├── main/
    │   ├── __init__.py
    │   └── commands.py    # Example command created by startproject
    └── inventory/
        ├── __init__.py
        ├── commands.py    # Your CLI commands
        └── ui.py          # Your visual components
```
