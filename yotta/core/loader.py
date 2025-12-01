import importlib
import rich_click as click
from yotta.conf import settings

class AppLoader:
    def __init__(self):
        self.apps = settings.INSTALLED_APPS

    def get_commands(self):
        """
        Scan all installed apps and return a dict {name: click_command}.
        """
        commands = {}

        for app_path in self.apps:
            # Try to import the 'commands' submodule of each app
            # Ex: if app='src.main', search 'src.main.commands'
            module_name = f"{app_path}.commands"
            
            try:
                mod = importlib.import_module(module_name)
            except ImportError as e:
                # If the commands.py module does not exist, ignore the app
                # But raise the error if it's not an import error (user code bug)
                if f"No module named '{module_name}'" in str(e):
                    continue
                raise e

            # Introspection : search for click.Command objects in the module
            for attr_name, attr_value in vars(mod).items():
                if isinstance(attr_value, click.Command):
                    # Use the name defined in the @command(name="...") decorator
                    cmd_name = attr_value.name or attr_name
                    commands[cmd_name] = attr_value

        return commands