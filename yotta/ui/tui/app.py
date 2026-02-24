from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label


class YottaApp(App):
    """
    The base class for all TUI interfaces in yotta.
    It pre-configures the shortcuts and the base theme.
    """

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("d", "toggle_dark", "Dark Theme"),
    ]

    def __init__(self, title: str = "yotta App", **kwargs):
        super().__init__(**kwargs)
        self.title = title

    def compose(self) -> ComposeResult:
        """
        Default method. If the user does not override compose(),
        we display an empty structure with Header/Footer.
        """
        yield Header(show_clock=True)
        yield self.get_content()
        yield Footer()

    def get_content(self) -> Label:
        """
        Override this method to insert widgets while keeping the default Header/Footer.
        """
        return Label("Override the `compose()` or `get_content()` method to display your widgets.")

    def action_toggle_dark(self) -> None:
        """Toggle between light and dark mode."""
        self.dark = not self.dark


yottaApp = YottaApp
