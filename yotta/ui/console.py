from typing import List, Optional, Callable, Any
from yotta.rich_ui import rich
from yotta.ui.theme import DEFAULT_THEME


class yottaConsole:
    """
    High-level console wrapper for yotta framework.

    Provides convenient methods for common UI operations using Rich components
    through the unified RichUI interface.
    """

    def __init__(self):
        self._console = rich.console(theme=DEFAULT_THEME)

    def write(self, text: str, style: str = None):
        """Affiche du texte simple."""
        self._console.print(text, style=style)

    # --- MESSAGE BLOCKS ---

    def header(self, title: str, subtitle: str = None):
        """Display a styled large header."""
        content = rich.text(subtitle, style="secondary") if subtitle else None
        self._console.print(rich.panel(
            content or "",
            title=f"[header]{title.upper()}[/]",
            border_style="primary",
            expand=False,
            padding=(1, 2)
        ))
        self._console.print()  # Spacer

    def success(self, msg: str):
        """Display a success message."""
        self._console.print(f"[bold bright_green]✔[/] {msg}")

    def error(self, msg: str):
        """Display an error message."""
        self._console.print(f"[bold bright_red]✖[/] {msg}")

    def warning(self, msg: str):
        """Display a warning message."""
        self._console.print(f"[bold bright_yellow]⚠[/] {msg}")

    def info(self, msg: str):
        """Display an info message."""
        self._console.print(f"[bold bright_blue]ℹ[/] {msg}")

    # --- COMPLEX COMPONENTS ---

    def table(self, columns: List[str], rows: List[List[str]], title: str = None):
        """
        Create and display a formatted table automatically.
        Usage: yotta.ui.table(["Nom", "Âge"], [["Alice", "25"], ["Bob", "30"]])
        """
        table = rich.table(title=title, header_style="bold bright_cyan", border_style="primary")

        for col in columns:
            table.add_column(col)

        for row in rows:
            # Convert everything to string to avoid Rich errors
            table.add_row(*[str(r) for r in row])

        self._console.print(table)
        self._console.print()

    def panel(self, content: str, title: str = None, style: str = "primary"):
        """Display an information panel."""
        self._console.print(rich.panel(content, title=title, border_style=style))

    # --- INTERACTIVITY ---

    def ask(self, question: str, default: str = None) -> str:
        """Wrapper around Rich Prompt."""
        from rich.prompt import Prompt
        return Prompt.ask(f"[primary]{question}[/]", default=default, console=self._console)

    def confirm(self, question: str, default: bool = True) -> bool:
        """Wrapper around Rich Confirm."""
        from rich.prompt import Confirm
        return Confirm.ask(f"[primary]{question}[/]", default=default, console=self._console)

    def prompt(self, question: str, type_: Callable = str, default: Any = None):
        """
        Prompt for input and optionally validate via a callable/type.
        """
        from rich.prompt import Prompt
        while True:
            value = Prompt.ask(f"[primary]{question}[/]", default=default, console=self._console)
            try:
                return type_(value) if callable(type_) else value
            except Exception as e:
                self.error(f"Invalid value: {e}")

    # --- LOADER / SPINNER ---

    def spinner(self, message: str = "Loading..."):
        """
        Context manager to display a spinner during a long operation.
        Usage: with yotta.ui.spinner("Processing..."): ...
        """
        return self._console.status(f"[bold]{message}[/]", spinner="dots12")

    def progress(self, description: str = "Working..."):
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

    def task(self, title: str, work: Callable[[], Any]):
        """
        Simple task runner helper: shows a spinner while executing the callable.
        """
        with self.spinner(title):
            return work()
