from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Confirm, Prompt
from yotta.ui.theme import DEFAULT_THEME

class yottaConsole:
    def __init__(self):
        self._console = Console(theme=DEFAULT_THEME)

    def write(self, text: str, style: str = None):
        """Affiche du texte simple."""
        self._console.print(text, style=style)

    # --- MESSAGE BLOCKS ---

    def header(self, title: str, subtitle: str = None):
        """Display a styled large header."""
        content = Text(subtitle, style="secondary") if subtitle else None
        self._console.print(Panel(
            content or "",
            title=f"[header]{title.upper()}[/]",
            border_style="primary",
            expand=False,
            padding=(1, 2)
        ))
        self._console.print()  # Spacer

    def success(self, msg: str):
        self._console.print(f"[success]✔[/] {msg}")

    def error(self, msg: str):
        self._console.print(f"[error]✖[/] {msg}")

    def warning(self, msg: str):
        self._console.print(f"[warning]⚠[/] {msg}")

    # --- COMPLEX COMPONENTS ---

    def table(self, columns: List[str], rows: List[List[str]], title: str = None):
        """
        Create and display a formatted table automatically.
        Usage: ctx.ui.table(["Nom", "Âge"], [["Alice", "25"], ["Bob", "30"]])
        """
        table = Table(title=title, header_style="header", border_style="primary")
        
        for col in columns:
            table.add_column(col)
            
        for row in rows:
            # Convert everything to string to avoid Rich errors
            table.add_row(*[str(r) for r in row])
            
        self._console.print(table)
        self._console.print()

    def panel(self, content: str, title: str = None, style: str = "primary"):
        """Display an information panel."""
        self._console.print(Panel(content, title=title, border_style=style))

    # --- INTERACTIVITY ---

    def ask(self, question: str, default: str = None) -> str:
        """Wrapper around Rich Prompt."""
        return Prompt.ask(f"[primary]{question}[/]", default=default, console=self._console)

    def confirm(self, question: str, default: bool = True) -> bool:
        """Wrapper around Rich Confirm."""
        return Confirm.ask(f"[primary]{question}[/]", default=default, console=self._console)

    # --- LOADER / SPINNER ---
    
    def spinner(self, message: str = "Loading..."):
        """
        Context manager to display a spinner during a long operation.
        Usage: with ctx.ui.spinner("Processing..."): ...
        """
        return self._console.status(f"[bold]{message}[/]", spinner="dots")