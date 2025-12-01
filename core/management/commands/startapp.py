import os

class StartAppCommand:
    def run(self, args):
        if not args:
            print("Error: You must provide an application name.")
            print("Usage: python manage.py startapp <nom_app>")
            return

        app_name = args[0]
        # By convention, we place the apps in src/
        base_dir = os.path.join(os.getcwd(), "src", app_name)

        if os.path.exists(base_dir):
            print(f"Error: The directory 'src/{app_name}' already exists.")
            return

        print(f"Creating application '{app_name}' in src/...")
        self.create_structure(base_dir, app_name)
        
        print(f"[SUCCESS] App '{app_name}' created.")
        print(f"⚠ Don't forget to add 'src.{app_name}' to INSTALLED_APPS in yotta_settings.py!")

    def create_structure(self, base_dir, app_name):
        os.makedirs(base_dir)
        
        # 1. __init__.py (empty)
        self.write_file(base_dir, "__init__.py", "")
        
        # 2. commands.py (An example command to start)
        self.write_file(base_dir, "commands.py", self.get_commands_template(app_name))
        
        # 3. ui.py (Place for specific visual components)
        self.write_file(base_dir, "ui.py", self.get_ui_template())

    def write_file(self, path, filename, content):
        with open(os.path.join(path, filename), 'w') as f:
            f.write(content)

    # --- TEMPLATES ---

    def get_commands_template(self, app_name):
        return f"""
from yotta.cli.decorators import command
from yotta.core.context import Context

@command(name="{app_name}_test")
def test_command(ctx: Context):
    \"\"\"Test command for the application {app_name}.\"\"\"
    ctx.ui.header("Application : {app_name}")
    ctx.ui.success("The command works!")
"""

    def get_ui_template(self):
        return """
from rich.panel import Panel

# Put here your reusable UI components for this app
def info_panel(content):
    return Panel(content, style="blue")
"""