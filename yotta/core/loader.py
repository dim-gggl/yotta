import importlib
import traceback

import rich_click as click
from rich.console import Console
from yotta.conf import settings


class DuplicateCommandNameError(RuntimeError):
    """Raised when two apps expose the same click command name under strict mode."""


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

    def get_commands(self) -> dict[str, click.Command]:
        """
        Scan all installed apps and return a dict {name: click_command}.
        """
        commands: dict[str, click.Command] = {}
        command_sources: dict[str, tuple[str, str]] = {}  # cmd_name -> (module_name, attribute_name)

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
                    if cmd_name in commands:
                        prev_module, prev_attr = command_sources.get(cmd_name, ("<unknown>", "<unknown>"))
                        msg = (
                            f"Duplicate command name '{cmd_name}' discovered. "
                            f"Both '{prev_module}:{prev_attr}' and '{module_name}:{attr_name}' define it. "
                            f"Keeping the last one ('{module_name}:{attr_name}')."
                        )
                        if self.strict:
                            raise DuplicateCommandNameError(msg)
                        self.logger.warn(msg)
                    commands[cmd_name] = attr_value
                    command_sources[cmd_name] = (module_name, attr_name)

        return commands
