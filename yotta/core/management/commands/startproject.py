"""Command module to scaffold a new yotta project structure."""

import os, time
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.console import Console
from yotta.ui.spinner import centered_spinner


console = Console()


class StartProjectCommand:
    """Command handler that creates a new yotta project with standard structure."""

    def run(self, args):
        """Execute the startproject command with the given arguments."""
        if not args:
            console.print(f"[error]✖[/] Error: You must provide a project name.")
            console.print(f"[warning]⚠[/] Usage: python -m yotta startproject <project_name>")
            return

        project_name = args[0]
        base_dir = os.path.join(os.getcwd(), project_name)

        if os.path.exists(base_dir):
            console.print(f"[error]✖[/] Error: The directory '{project_name}' already exists.")
            return

        console.clear()
        console.print("\n" * 2)
        with Live(
            centered_spinner(
                message=Text(
                    f"Project creation at {base_dir}", 
                    style="bold orange_red1"
                )
            ),
            refresh_per_second=10, 
            transient=True
        ) as live:
            time.sleep(4)
            self.create_structure(base_dir, project_name)
        console.print(f"[green]✔[/] Success! cd {project_name} && python manage.py\n\n")

    def create_structure(self, base_dir, project_name):  # noqa: ARG002
        """Create the directory structure and boilerplate files for a new project."""
        # 1. Création des dossiers
        os.makedirs(os.path.join(base_dir, project_name, "main"))
        
        # 2. Création de manage.py
        self.write_file(base_dir, "manage.py", self.get_manage_py_template())
        
        # 3. Création des settings
        self.write_file(base_dir, "settings.py", self.get_settings_template())
        
        # 4. Fichiers __init__.py pour faire des packages
        self.write_file(os.path.join(base_dir, project_name), "__init__.py", "")
        self.write_file(os.path.join(base_dir, project_name, "main"), "__init__.py", "")

        # 5. Exemple de commande utilisateur
        self.write_file(os.path.join(base_dir, project_name, "main"), "commands.py", self.get_commands_template())

    def write_file(self, path, filename, content):
        """Write content to a file at the specified path."""
        with open(os.path.join(path, filename), 'w', encoding='utf-8') as f:
            f.write(content)

    # --- TEMPLATES (Hardcodés pour le MVP) ---
    
    def get_manage_py_template(self):
        return """#!/usr/bin/env python
import os
import sys
from yotta.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("YOTTA_SETTINGS_MODULE", "settings.py")
    execute_from_command_line(sys.argv)
"""

    def get_settings_template(self):
        return f"""
# Configuration yotta
INSTALLED_APPS = [
    'src.main',
]

THEME = 'default'

ROOT_DIR = {os.getcwd()}
"""

    def get_commands_template(self):
        return """
from yotta.cli.decorators import command
from yotta.core.context import Context

@command(name="hello")
def hello_world(ctx: Context):
    ctx.ui.header("Hello yotta")
    ctx.ui.success("Your first app works!")
"""