import importlib.util
import os
from typing import Any, Dict, List, Optional

import rich_click as click
from rich.console import Console


class StartCommandCommand:
    """Interactively scaffold a new CLI command inside an installed app."""

    def __init__(self) -> None:
        self.console = Console()

    def run(self, args: List[str], app: Optional[str] = None) -> None:
        try:
            from yotta.conf import settings
        except ImportError as exc:  # pragma: no cover - defensive guard for missing settings
            self.console.print(
                "[bold red]Error:[/] "
                f"Unable to load settings: {exc}"
            )
            return

        installed_apps = getattr(settings, "INSTALLED_APPS", [])
        if not installed_apps:
            self.console.print(
                "[bold red]Error:[/] No INSTALLED_APPS configured. "
                "Run this inside a yotta project."
            )
            return

        app_path = app or self._select_app(installed_apps)
        if not app_path:
            self.console.print(
                "[yellow]No app selected. "
                "Nothing was created.[/]"
            )
            return

        commands_file = self._resolve_commands_file(app_path)
        if commands_file is None:
            self.console.print(
                "[bold red]Error:[/] Could not resolve a "
                f"module path for '{app_path}'."
            )
            return

        os.makedirs(os.path.dirname(commands_file), exist_ok=True)

        if not os.path.exists(commands_file):
            self._write_file(commands_file, self._base_commands_file())
            self.console.print(f"[green]Created[/] {commands_file}")
        else:
            self._ensure_imports(commands_file)

        config = self._prompt_command_config()
        if config is None:
            self.console.print("[yellow]Command creation cancelled.[/]")
            return

        command_block = self._render_command_block(config)

        with open(commands_file, "a", encoding="utf-8") as f:
            f.write(command_block)

        self.console.print(f"[green]Added[/] command '{config['name']}' to {commands_file}")

    def _select_app(self, installed_apps: List[str]) -> Optional[str]:
        if len(installed_apps) == 1:
            self.console.print(f"Using app: {installed_apps[0]}")
            return installed_apps[0]

        self.console.print("Select the app where the command should live:")
        for idx, app in enumerate(installed_apps, start=1):
            self.console.print(f"  {idx}) {app}")

        while True:
            choice = input(f"Choose 1-{len(installed_apps)} (leave empty to cancel): ").strip()
            if not choice:
                return None
            if choice.isdigit():
                index = int(choice)
                if 1 <= index <= len(installed_apps):
                    return installed_apps[index - 1]
            self.console.print("Invalid selection, try again.")

    def _resolve_commands_file(self, app_path: str) -> Optional[str]:
        spec = importlib.util.find_spec(app_path)
        if spec is None or not spec.submodule_search_locations:
            return None

        app_dir = list(spec.submodule_search_locations)[0]
        return os.path.join(app_dir, "commands.py")

    def _prompt_command_config(self) -> Optional[Dict[str, Any]]:
        name = self._prompt_required("Command name (as used on CLI)")
        if not name:
            return None

        help_text = input("Description (optional): ").strip()

        arguments: List[Dict[str, str]] = []
        while self._confirm("Add a positional argument?"):
            arg_name = self._prompt_identifier("  Argument name")
            arguments.append({"name": arg_name, "param": arg_name})

        options: List[Dict[str, Any]] = []
        while self._confirm("Add an option or flag?"):
            option_name = self._prompt_identifier("  Option name (without dashes)")
            short_flag = input("  Short flag (single letter, optional): ").strip().lstrip("-")
            is_flag = self._confirm("  Is this a boolean flag (no value)?")
            default = None
            if not is_flag:
                default_raw = input("  Default value (leave empty for none): ").strip()
                default = default_raw if default_raw else None
            option_help = input("  Help text (optional): ").strip()
            options.append(
                {
                    "name": option_name,
                    "param": self._to_identifier(option_name),
                    "short": short_flag[0] if short_flag else None,
                    "is_flag": is_flag,
                    "default": default,
                    "help": option_help,
                }
            )

        return {
            "name": name,
            "function_name": self._to_identifier(name),
            "help": help_text,
            "arguments": arguments,
            "options": options,
        }

    def _render_command_block(self, config: Dict[str, Any]) -> str:
        lines = ["", ""]
        lines.append(self._command_decorator(config))

        for arg in config["arguments"]:
            lines.append(f'@argument("{arg["name"]}")')

        for opt in config["options"]:
            lines.append(self._option_decorator(opt))

        signature_parts = ["yotta: YottaContext"]
        signature_parts.extend(arg["param"] for arg in config["arguments"])
        signature_parts.extend(opt["param"] for opt in config["options"])
        lines.append(f"def {config['function_name']}({', '.join(signature_parts)}):")

        if config["help"]:
            lines.append(f'    """{self._escape_quotes(config["help"])}"""')

        lines.append(f'    yotta.ui.header("{self._escape_quotes(config["name"])}")')
        lines.append("    # TODO: implement your command logic")
        lines.append("    ...")
        lines.append("")

        return "\n".join(lines)

    def _command_decorator(self, config: Dict[str, Any]) -> str:
        help_part = f', help="{self._escape_quotes(config["help"])}"' if config["help"] else ""
        return f'@command(name="{self._escape_quotes(config["name"])}"{help_part})'

    def _option_decorator(self, opt: Dict[str, Any]) -> str:
        flags = []
        if opt["short"]:
            flags.append(f'"-{opt["short"]}"')
        flags.append(f'"--{opt["name"]}"')

        params = []
        if opt["is_flag"]:
            params.append("is_flag=True")
            params.append("default=False")
        elif opt["default"] is not None:
            params.append(f'default="{self._escape_quotes(opt["default"])}"')
            params.append("show_default=True")

        if opt["help"]:
            params.append(f'help="{self._escape_quotes(opt["help"])}"')

        joined = ", ".join(flags + params)
        return f"@option({joined})"

    def _prompt_identifier(self, label: str) -> str:
        raw = self._prompt_required(label)
        ident = self._to_identifier(raw)
        if ident != raw:
            self.console.print(f"  Using '{ident}' as the parameter name.")
        return ident

    def _prompt_required(self, label: str) -> str:
        while True:
            value = input(f"{label}: ").strip()
            if value:
                return value
            self.console.print("  Please provide a value.")

    def _confirm(self, label: str, default: bool = False) -> bool:
        suffix = "[Y/n]" if default else "[y/N]"
        value = input(f"{label} {suffix}: ").strip().lower()
        if not value:
            return default
        return value in ("y", "yes")

    def _escape_quotes(self, value: str) -> str:
        return value.replace('"', '\\"')

    def _base_commands_file(self) -> str:
        return "from yotta.cli.decorators import command, argument, option\nfrom yotta.core.context import YottaContext\n\n"

    def _ensure_imports(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        additions = []

        if "from yotta.cli.decorators import" not in content:
            additions.append("from yotta.cli.decorators import command, argument, option")

        if "from yotta.core.context import YottaContext" not in content:
            additions.append("from yotta.core.context import YottaContext")

        if additions:
            content = "\n".join(additions + ["", content])
            self._write_file(path, content)

    def _write_file(self, path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _to_identifier(self, raw: str) -> str:
        return raw.strip().replace(" ", "_").replace("-", "_")


@click.command(name="startcommand", help="Interactively scaffold a new command in an installed app.")
@click.option("--app", "app_name", default=None, help="Preselect the target app (module path).")
def startcommand_command(app_name: Optional[str] = None) -> None:
    """
    Click entry point to launch the interactive command creator.
    """
    StartCommandCommand().run([], app=app_name)
