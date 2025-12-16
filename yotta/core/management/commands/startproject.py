"""Command module to scaffold a new yotta project structure."""

import os
import stat
import time
import rich_click as click
from rich.live import Live
from rich.text import Text
from rich.console import Console
from yotta.ui.spinner import centered_spinner


console = Console()


@click.command(name="startproject", help="Scaffold a new yotta project.")
@click.argument("project_name")
@click.option(
    "--dst",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, readable=True, resolve_path=True),
    default=".",
    help="Destination directory where the project will be created.",
)
@click.option(
    "--settings",
    "settings_module",
    default="settings",
    help="Settings module to set as default in manage.py and .env.example.",
)
@click.option("--force", is_flag=True, help="Overwrite existing files if the project directory already exists.")
def startproject_command(project_name: str, dst: str, settings_module: str, force: bool) -> None:
    creator = StartProjectCommand()
    creator.run(project_name, dst, settings_module, force)


class StartProjectCommand:
    """Command handler that creates a new yotta project with standard structure."""

    def run(self, project_name: str, dst: str, settings_module: str, force: bool) -> None:
        base_dir = os.path.join(dst, project_name)

        if os.path.exists(base_dir) and not force:
            console.print(f"[bold red]✖[/] Error: The directory '{base_dir}' already exists. Use --force to overwrite.")
            return

        console.print(f"Creating project '{project_name}' in {base_dir}")
        console.print()
        os.makedirs(base_dir, exist_ok=True)
        with Live(
            centered_spinner(
                message=Text(
                    f"Creating project at {base_dir}",
                    style="bold orange_red1"
                )
            ),
            refresh_per_second=10,
            transient=True
        ):
            time.sleep(1)
            self.create_structure(base_dir, project_name, settings_module, force)
        console.print(f"[green]✔[/] Success! cd {project_name} && python manage.py\n")

    def create_structure(self, base_dir: str, project_name: str, settings_module: str, force: bool) -> None:
        """Create the directory structure and boilerplate files for a new project."""
        pkg_dir = os.path.join(base_dir, project_name)
        main_dir = os.path.join(pkg_dir, "main")
        os.makedirs(main_dir, exist_ok=True)

        # Files at project root
        self.write_file(base_dir, "manage.py", self.get_manage_py_template(settings_module), force=force, make_executable=True)
        self.write_file(base_dir, "settings.py", self.get_settings_template(project_name, base_dir), force=force)
        self.write_file(base_dir, "pyproject.toml", self.get_pyproject_template(project_name), force=force)
        self.write_file(base_dir, ".env.example", self.get_env_example(settings_module), force=force)
        self.write_file(base_dir, "__init__.py", "", force=force)

        # Package init files
        self.write_file(pkg_dir, "__init__.py", "", force=force)
        self.write_file(main_dir, "__init__.py", "", force=force)

        # Example command
        self.write_file(main_dir, "commands.py", self.get_commands_template(), force=force)

    def write_file(self, path: str, filename: str, content: str, force: bool = False, make_executable: bool = False) -> None:
        """Write content to a file at the specified path."""
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path) and not force:
            console.print(f"[yellow]Skipping[/] existing file {full_path}")
            return

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        if make_executable:
            current_mode = os.stat(full_path).st_mode
            os.chmod(full_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    # --- TEMPLATES ---

    def get_manage_py_template(self, settings_module: str) -> str:
        return f"""#!/usr/bin/env python3
import os
import sys
from yotta.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("YOTTA_SETTINGS_MODULE", "{settings_module}")
    execute_from_command_line(sys.argv)
"""

    def get_settings_template(self, project_name: str, base_dir: str) -> str:
        return f"""
# yotta settings
INSTALLED_APPS = [
    "{project_name}.main",
]

THEME = "default"

ROOT_DIR = "{os.path.abspath(base_dir)}"
"""

    def get_pyproject_template(self, project_name: str) -> str:
        return f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "A yotta project."
readme = "README.md"
requires-python = ">=3.10"
dependencies = ["yotta"]

[tool.uv]
"""

    def get_env_example(self, settings_module: str) -> str:
        return f"YOTTA_SETTINGS_MODULE={settings_module}\n"

    def get_commands_template(self) -> str:
        return """
from yotta.cli.decorators import command
from yotta.core.context import YottaContext


@command(name="hello")
def hello_world(yotta: YottaContext):
    \"\"\"Simple example command shipped with your new project.\"\"\"
    yotta.ui.header("Hello from yotta")
    yotta.ui.success("Your project is ready. Edit this command to get started!")
"""
