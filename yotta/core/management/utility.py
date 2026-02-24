import sys
from importlib.metadata import version as _pkg_version

import rich_click as click
from rich.console import Console

from yotta.core.loader import AppLoader, DuplicateCommandNameError
from yotta.core.management.commands.check import check_command
from yotta.core.management.commands.completion import completion_command
from yotta.core.management.commands.startapp import startapp_command
from yotta.core.management.commands.startcommand import startcommand_command
from yotta.core.management.commands.startproject import startproject_command

_BASE_COMMANDS = {
    "startproject": startproject_command,
    "startapp": startapp_command,
    "startcommand": startcommand_command,
    "check": check_command,
    "completion": completion_command,
}


class YottaUtility:
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]
        self.console = Console()

    def build_cli(self) -> click.Group:
        """Build and return the root Click group without invoking it."""
        subcommand = None
        for arg in self.argv[1:]:
            if arg.startswith("-"):
                continue
            subcommand = arg
            break

        settings_error = None
        discovery_error = None
        discovered_commands: dict[str, click.Command] = {}
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
        except DuplicateCommandNameError as exc:
            discovery_error = str(exc)

        pkg_version = _pkg_version("yotta")

        @click.group(invoke_without_command=True)
        @click.version_option(pkg_version, prog_name="yotta", message="%(prog)s %(version)s")
        @click.option("--quiet", is_flag=True, help="Silence loader warnings.")
        @click.option("--verbose", is_flag=True, help="Show loader details.")
        @click.option("--strict", is_flag=True, help="Fail fast on missing or broken commands modules.")
        @click.pass_context
        def cli(ctx, quiet, verbose, strict):
            if ctx.invoked_subcommand is None:
                click.echo(ctx.get_help())
                if settings_error:
                    click.echo(f"\n[Settings error] {settings_error}")
                if discovery_error:
                    click.echo(f"\n[Discovery error] {discovery_error}")

        for name, cmd in _BASE_COMMANDS.items():
            cli.add_command(cmd, name=name)

        if settings_error and subcommand and subcommand not in _BASE_COMMANDS:
            self.console.print(f"[bold red]Settings error:[/] {settings_error}")
            self.console.print("Set YOTTA_SETTINGS_MODULE (or YOTTA_ENV / .env) before running commands.")
            return cli
        if discovery_error:
            self.console.print(f"[bold red]Discovery error:[/] {discovery_error}")
            raise SystemExit(1)

        for name, cmd in discovered_commands.items():
            cli.add_command(cmd, name=name)

        return cli

    @property
    def prog_name(self) -> str:
        invoked = self.argv[0] if self.argv else ""
        if invoked.endswith("manage.py"):
            return "manage.py"
        return "yotta"

    def execute(self):
        cli = self.build_cli()
        cli(prog_name=self.prog_name)


yottaUtility = YottaUtility


def execute_from_command_line(argv=None):
    utility = YottaUtility(argv)
    utility.execute()
