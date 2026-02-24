from collections.abc import Callable
from typing import Any

from rich.progress import Progress, TaskID
from rich.prompt import Confirm, Prompt
from rich.status import Status
from rich.theme import Theme

import yotta.conf
from yotta.rich_ui import rich
from yotta.ui.theme import resolve_theme


class YottaConsole:
    """
    High-level console wrapper for yotta framework.

    Provides convenient methods for common UI operations using Rich components
    through the unified RichUI interface.
    """

    def __init__(self, theme: str | None = None) -> None:
        """
        Create a yotta console.

        If `theme` is not provided, yotta will try to read `THEME` from project settings
        and fall back to the default theme when settings are unavailable or invalid.
        """
        theme_name = theme
        if not theme_name:
            try:
                theme_name = getattr(yotta.conf.settings, "THEME", "default")
            except Exception:
                theme_name = "default"

        self._theme_name = str(theme_name) if theme_name is not None else "default"
        self._theme = resolve_theme(self._theme_name)
        self._console = rich.console(theme=self._theme)

    def write(self, text: str, style: str | None = None) -> None:
        """Display plain text."""
        self._console.print(text, style=style)

    # --- MESSAGE BLOCKS ---

    def header(self, title: str, subtitle: str | None = None) -> None:
        """Display a styled large header."""
        content = rich.text(subtitle, style="secondary") if subtitle else None
        self._console.print(
            rich.panel(
                content or "", title=f"[header]{title.upper()}[/]", border_style="primary", expand=False, padding=(1, 2)
            )
        )
        self._console.print()

    def success(self, msg: str) -> None:
        """Display a success message."""
        self._console.print(f"[success]✔[/] {msg}")

    def error(self, msg: str) -> None:
        """Display an error message."""
        self._console.print(f"[error]✖[/] {msg}")

    def warning(self, msg: str) -> None:
        """Display a warning message."""
        self._console.print(f"[warning]⚠[/] {msg}")

    def info(self, msg: str) -> None:
        """Display an info message."""
        self._console.print(f"[info]ℹ[/] {msg}")

    # --- COMPLEX COMPONENTS ---

    def table(self, columns: list[str], rows: list[list[str]], title: str | None = None) -> None:
        """
        Create and display a formatted table automatically.
        Usage: yotta.ui.table(["Name", "Age"], [["Alice", "25"], ["Bob", "30"]])
        """
        table = rich.table(title=title, header_style="secondary", border_style="primary")

        for col in columns:
            table.add_column(col)

        for row in rows:
            table.add_row(*[str(r) for r in row])

        self._console.print(table)
        self._console.print()

    def panel(self, content: str, title: str | None = None, style: str = "primary") -> None:
        """Display an information panel."""
        self._console.print(rich.panel(content, title=title, border_style=style))

    # --- INTERACTIVITY ---

    def ask(self, question: str, default: str | None = None) -> str:
        """Wrapper around Rich Prompt."""
        result = Prompt.ask(f"[primary]{question}[/]", default=default, console=self._console)
        return result or ""

    def confirm(self, question: str, default: bool = True) -> bool:
        """Wrapper around Rich Confirm."""
        return Confirm.ask(f"[primary]{question}[/]", default=default, console=self._console)

    def prompt(self, question: str, type_: Callable = str, default: Any = None) -> Any:
        """Prompt for input and optionally validate via a callable/type."""
        while True:
            value = Prompt.ask(f"[primary]{question}[/]", default=default, console=self._console)
            try:
                return type_(value) if callable(type_) else value
            except Exception as e:
                self.error(f"Invalid value: {e}")

    # --- LOADER / SPINNER ---

    def spinner(self, message: str = "Loading...") -> Status:
        """
        Context manager to display a spinner during a long operation.
        Usage: with yotta.ui.spinner("Processing..."): ...
        """
        return self._console.status(f"[bold]{message}[/]", spinner="dots12")

    def progress(self, description: str = "Working...") -> tuple[Progress, TaskID]:
        """
        Create a Rich progress bar and return a task ID for manual updates.
        Usage:
            progress, task = yotta.ui.progress("Downloading")
            for i in range(...):
                progress.update(task, advance=1)
        """
        progress = rich.progress(
            transient=True,
            expand=True,
        )
        task = progress.add_task(description, total=100)
        return progress, task

    def task(self, title: str, work: Callable[[], Any]) -> Any:
        """Simple task runner helper: shows a spinner while executing the callable."""
        with self.spinner(title):
            return work()

    @property
    def theme_name(self) -> str:
        """Return the selected theme name (after normalization)."""
        return self._theme_name

    @property
    def theme(self) -> Theme:
        """Return the resolved Rich Theme instance."""
        return self._theme


yottaConsole = YottaConsole
