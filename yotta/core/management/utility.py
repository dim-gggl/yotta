import sys
import os
import rich_click as click
from rich.console import Console
from yotta.core.management.commands.startproject import startproject_command
from yotta.core.management.commands.startapp import startapp_command
from yotta.core.management.commands.startcommand import startcommand_command


class yottaUtility:
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.console = Console()

    def execute(self):
        subcommand = None
        for arg in self.argv[1:]:
            if arg.startswith("-"):
                continue
            subcommand = arg
            break

        base_commands = {
            "startproject": startproject_command,
            "startapp": startapp_command,
            "startcommand": startcommand_command,
        }

        # 1. Management of system commands and user commands (Runtime)
        from yotta.core.loader import AppLoader

        settings_error = None
        discovered_commands = {}
        loader_kwargs = {
            "quiet": "--quiet" in self.argv,
            "verbose": "--verbose" in self.argv,
            "strict": "--strict" in self.argv,
        }
        try:
            loader = AppLoader(**loader_kwargs)
            discovered_commands = loader.get_commands()
        except ImportError as exc:
            settings_error = str(exc)

        # Root Click Group
        @click.group(invoke_without_command=True)
        @click.option("--quiet", is_flag=True, help="Silence loader warnings.")
        @click.option("--verbose", is_flag=True, help="Show loader details.")
        @click.option("--strict", is_flag=True, help="Fail fast on missing or broken commands modules.")
        @click.pass_context
        def cli(ctx, quiet, verbose, strict):
            if ctx.invoked_subcommand is None:
                click.echo(ctx.get_help())
                if settings_error:
                    click.echo(f"\n[Settings error] {settings_error}")

        # Attach bootstrap commands
        for name, cmd in base_commands.items():
            cli.add_command(cmd, name=name)

        # Guard: if settings are missing and user asks for non-bootstrap command, show error early
        if settings_error and subcommand and subcommand not in base_commands:
            self.console.print(f"[bold red]Settings error:[/] {settings_error}")
            self.console.print("Set YOTTA_SETTINGS_MODULE (or YOTTA_ENV / .env) before running commands.")
            return

        # Attach discovered commands
        for name, cmd in discovered_commands.items():
            cli.add_command(cmd, name=name)

        # Launch Click
        cli(prog_name="manage.py")

def execute_from_command_line(argv=None):
    utility = yottaUtility(argv)
    utility.execute()
