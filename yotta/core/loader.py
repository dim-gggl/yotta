import importlib
import traceback

import rich_click as click
from rich.console import Console
from yotta.conf import settings


class _LoaderLogger:
    def __init__(self, quiet: bool = False, verbose: bool = False):
        self.console = Console()
        self.quiet = quiet
        self.verbose = verbose

    def warn(self, message: str) -> None:
        if not self.quiet:
            self.console.print(f"[yellow]Warning:[/] {message}")

    def info(self, message: str) -> None:
        if self.verbose and not self.quiet:
            self.console.print(f"[blue]Info:[/] {message}")

    def error(self, message: str) -> None:
        self.console.print(f"[bold red]Error:[/] {message}")


class AppLoader:
    def __init__(self, quiet: bool = False, verbose: bool = False, strict: bool = False):
        self.apps = settings.INSTALLED_APPS
        self.logger = _LoaderLogger(quiet=quiet, verbose=verbose)
        self.strict = strict

    def get_commands(self):
        """
        Scan all installed apps and return a dict {name: click_command}.
        """
        commands = {}

        for app_path in self.apps:
            module_name = f"{app_path}.commands"
            try:
                mod = importlib.import_module(module_name)
                self.logger.info(f"Loaded commands module: {module_name}")
            except ImportError as e:
                if f"No module named '{module_name}'" in str(e):
                    msg = f"No commands.py found for app '{app_path}'. Skipping."
                    if self.strict:
                        raise ImportError(msg)
                    self.logger.warn(msg)
                    continue
                # unexpected ImportError inside module
                if self.strict:
                    raise
                self.logger.error(f"Error importing {module_name}: {e}")
                self.logger.error(traceback.format_exc())
                continue

            # Introspection : search for click.Command objects in the module
            for attr_name, attr_value in vars(mod).items():
                if isinstance(attr_value, click.Command):
                    cmd_name = attr_value.name or attr_name
                    commands[cmd_name] = attr_value

        return commands
