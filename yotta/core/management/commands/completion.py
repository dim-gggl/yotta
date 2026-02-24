from __future__ import annotations

import re

import rich_click as click
from rich.console import Console
from rich.panel import Panel


def _complete_var(command_str: str) -> str:
    """Derive the Click completion env-var name from a command string.

    Click uses the *prog_name* (last token of the invocation) to build
    ``_<PROG>_COMPLETE``.  Non-alphanumeric characters become ``_``.

    Examples::

        "yotta"             -> "_YOTTA_COMPLETE"
        "python manage.py"  -> "_MANAGE_PY_COMPLETE"
        "my-cli"            -> "_MY_CLI_COMPLETE"
    """
    prog = command_str.strip().rsplit(None, 1)[-1]
    sanitized = re.sub(r"[^a-zA-Z0-9]", "_", prog).upper()
    return f"_{sanitized}_COMPLETE"


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
    default="yotta",
    show_default=True,
    help="Command used to invoke yotta (e.g. 'yotta' or 'python manage.py').",
)
def completion_command(shell: str, command_str: str) -> None:
    """
    Click completion is activated by evaluating a shell snippet that sets
    ``_<PROG>_COMPLETE`` for the selected shell.

    The variable name is derived automatically from ``--command``:
    ``yotta`` → ``_YOTTA_COMPLETE``, ``python manage.py`` → ``_MANAGE_PY_COMPLETE``.
    """
    console = Console()
    shell = shell.lower().strip()

    mode_map = {
        "bash": "bash_source",
        "zsh": "zsh_source",
        "fish": "fish_source",
    }
    mode = mode_map[shell]
    env_var = _complete_var(command_str)

    if shell == "fish":
        snippet = f"{env_var}={mode} {command_str} | source"
    else:
        snippet = f'eval "$({env_var}={mode} {command_str})"'

    message = (
        "Add this line to your shell config (e.g. `~/.zshrc`, `~/.bashrc`, `~/.config/fish/config.fish`).\n\n"
        f"[bold]{snippet}[/]\n\n"
        f"The completion variable `{env_var}` is derived from the `--command` value."
    )
    console.print(Panel(message, title="Shell Completion", border_style="cyan"))
