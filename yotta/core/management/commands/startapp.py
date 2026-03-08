import os
import re
from pathlib import Path

import rich_click as click
from rich.console import Console

console = Console()


def find_project_root(start: str | None = None) -> Path | None:
    """Walk up from *start* (defaults to cwd) to locate the yotta project root.

    Detection order per directory:
      1. ``manage.py`` whose content references yotta.
      2. ``pyproject.toml`` listing yotta as a dependency alongside ``settings.py``.
    """
    current = Path(start or os.getcwd()).resolve()

    for directory in (current, *current.parents):
        manage_py = directory / "manage.py"
        if manage_py.is_file():
            try:
                content = manage_py.read_text(encoding="utf-8")
                if "yotta" in content:
                    return directory
            except OSError as ex:
                console.print(f"[bold red]✖ Error[/]: {ex}")
                continue

        pyproject = directory / "pyproject.toml"
        settings_py = directory / "settings.py"
        if pyproject.is_file() and settings_py.is_file():
            try:
                content = pyproject.read_text(encoding="utf-8")
                if '"yotta"' in content or "'yotta'" in content:
                    return directory
            except OSError:
                continue

    return None


def get_project_name(project_root: Path) -> str | None:
    """Derive the project name from ``pyproject.toml`` at *project_root*.

    Returns ``None`` when the file is absent or unparseable.
    """
    pyproject = project_root / "pyproject.toml"
    if pyproject.is_file():
        try:
            content = pyproject.read_text(encoding="utf-8")
            match = re.search(r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                return match.group(1)
        except OSError:
            pass
    return None


@click.command(name="startapp", help="Create a new app inside the current project package.")
@click.argument("app_name")
@click.option(
    "--dst",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=None,
    help="Destination project package directory. Defaults to auto-detected <project_root>/<project_name>/.",
)
@click.option("--force", is_flag=True, help="Overwrite if the app directory already exists.")
def startapp_command(app_name: str, dst: str | None, force: bool) -> None:
    creator = StartAppCommand()
    creator.run(app_name, dst, force)


class StartAppCommand:
    def run(self, app_name: str, dst: str | None, force: bool) -> None:
        if dst:
            package_root = dst
            project_name = os.path.basename(package_root)
        else:
            project_root = find_project_root()
            if not project_root:
                console.print(
                    "[bold red]✖[/] Could not locate the project root.\n"
                    "  Run this command from inside a yotta project "
                    "(a directory tree containing manage.py),\n"
                    "  or pass --dst explicitly."
                )
                return

            project_name = get_project_name(project_root) or project_root.name
            package_root = str(project_root / project_name)

            # PEP 508: hyphens and underscores are interchangeable
            if not os.path.isdir(package_root):
                alt = str(project_root / project_name.replace("-", "_"))
                if os.path.isdir(alt):
                    project_name = project_name.replace("-", "_")
                    package_root = alt

            if not os.path.isdir(package_root):
                console.print(
                    f"[bold red]✖[/] Package directory '{package_root}' not found.\n"
                    f"  Expected a '{project_name}/' directory inside '{project_root}'.\n"
                    "  Pass --dst to specify the target directory explicitly."
                )
                return

        base_dir = os.path.join(package_root, app_name)

        if os.path.exists(base_dir) and not force:
            console.print(f"[bold red]✖[/] Error: The directory '{base_dir}' already exists. Use --force to overwrite.")
            return

        console.print(f"Creating application '{app_name}' in {package_root}...")
        self.create_structure(base_dir, app_name, force)

        console.print(f"[green]✔[/] App '{app_name}' created.")
        console.print(f"[yellow]⚠[/] Add '{project_name}.{app_name}' to INSTALLED_APPS in settings.py.")

    def create_structure(self, base_dir: str, app_name: str, force: bool) -> None:
        os.makedirs(base_dir, exist_ok=True)

        # 1. __init__.py (empty)
        self.write_file(base_dir, "__init__.py", "", force=force)

        # 2. commands.py (An example command to start)
        self.write_file(base_dir, "commands.py", self.get_commands_template(app_name), force=force)

        # 3. ui.py (Place for specific visual components)
        self.write_file(base_dir, "ui.py", self.get_ui_template(), force=force)

    def write_file(self, path: str, filename: str, content: str, force: bool = False) -> None:
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path) and not force:
            console.print(f"[yellow]Skipping[/] existing file {full_path}")
            return
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    # --- TEMPLATES ---

    def get_commands_template(self, app_name: str) -> str:
        return f"""
import time

from yotta.cli.decorators import command
from yotta.core.context import YottaContext


@command(name="{app_name}_example")
def example_command(yotta: YottaContext):
    \"\"\"Example command for the application {app_name}.\"\"\"
    yotta.ui.header("Application: {app_name}")
    yotta.ui.success("The command works!")
    yotta.ui.table(
        columns=["ID", "Name", "Email"],
        rows=[["1", "Jane Doe", "jane.doe@example.com"]],
        title="Users"
    )
    with yotta.ui.spinner("Processing..."):
        time.sleep(1)
    if yotta.ui.confirm("Do you want to continue?"):
        yotta.ui.success("Continuing...")
    else:
        yotta.ui.warning("Operation cancelled.")

"""

    def get_ui_template(self) -> str:
        return """
from rich.panel import Panel


# Put your reusable UI components for this app here
def info_panel(content):
    return Panel(content, style="blue")
"""
