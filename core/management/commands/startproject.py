"""Command module to scaffold a new yotta project structure."""

import os


class StartProjectCommand:
    """Command handler that creates a new yotta project with standard structure."""

    def run(self, args):
        """Execute the startproject command with the given arguments."""
        if not args:
            print("Erreur: Vous devez fournir un nom de projet.")
            print("Usage: python -m yotta startproject <nom_du_projet>")
            return

        project_name = args[0]
        base_dir = os.path.join(os.getcwd(), project_name)

        if os.path.exists(base_dir):
            print(f"Erreur: Le dossier '{project_name}' existe déjà.")
            return

        print(f"Création du projet yotta '{project_name}'...")
        self.create_structure(base_dir, project_name)
        print(f"Succès ! cd {project_name} && python manage.py")

    def create_structure(self, base_dir, project_name):  # noqa: ARG002
        """Create the directory structure and boilerplate files for a new project."""
        # 1. Création des dossiers
        os.makedirs(os.path.join(base_dir, "src", "main"))
        
        # 2. Création de manage.py
        self.write_file(base_dir, "manage.py", self.get_manage_py_template())
        
        # 3. Création des settings
        self.write_file(base_dir, "yotta_settings.py", self.get_settings_template())
        
        # 4. Fichiers __init__.py pour faire des packages
        self.write_file(os.path.join(base_dir, "src"), "__init__.py", "")
        self.write_file(os.path.join(base_dir, "src", "main"), "__init__.py", "")

        # 5. Exemple de commande utilisateur
        self.write_file(os.path.join(base_dir, "src", "main"), "commands.py", self.get_commands_template())

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
    os.environ.setdefault("yotta_SETTINGS_MODULE", "yotta_settings")
    execute_from_command_line(sys.argv)
"""

    def get_settings_template(self):
        return """
# Configuration yotta
INSTALLED_APPS = [
    'src.main',
]

THEME = 'default'
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