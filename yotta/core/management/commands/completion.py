from __future__ import annotations

import rich_click as click
from rich.console import Console
from rich.panel import Panel


@click.command(name="completion", help="Print shell completion instructions (Click).")
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish"], case_sensitive=False),
    required=True,
    help="Target shell for completion script source snippet.",
)
@click.option(
    "--command",
    "command_str",
    default="python manage.py",
    show_default=True,
    help="Command used to invoke yotta (e.g. 'python manage.py' or 'yotta').",
)
def completion_command(shell: str, command_str: str) -> None:
    """
    Click completion is activated by evaluating a shell snippet that sets
    `_<PROG>_COMPLETE` for the selected shell.

    Since yotta uses `prog_name='manage.py'` for Django-like output, the env var is
    `_MANAGE_PY_COMPLETE` even when you run via the `yotta` entry point.
    """
    console = Console()
    shell = shell.lower().strip()

    mode_map = {
        "bash": "bash_source",
        "zsh": "zsh_source",
        "fish": "fish_source",
    }
    mode = mode_map[shell]

    if shell == "fish":
        snippet = f"_MANAGE_PY_COMPLETE={mode} {command_str} | source"
    else:
        snippet = f'eval "$(_MANAGE_PY_COMPLETE={mode} {command_str})"'

    message = (
        "Add this line to your shell config (e.g. `~/.zshrc`, `~/.bashrc`, `~/.config/fish/config.fish`).\n\n"
        f"[bold]{snippet}[/]\n\n"
        "Notes:\n"
        "- The completion variable name is `_MANAGE_PY_COMPLETE` because yotta formats help like `manage.py`.\n"
        "- Use `--command yotta` if you invoke yotta via the installed entry point."
    )
    console.print(Panel(message, title="Shell Completion", border_style="cyan"))

