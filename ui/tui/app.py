from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding

class yottaApp(App):
    """
    The base class for all TUI interfaces in yotta.
    It pre-configures the shortcuts and the base theme.
    """
    
    # Default CSS configuration to resemble yotta
    CSS = """
    Screen {
        background: $surface;
    }
    """

    # Global bindings (available everywhere in the app)
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
        yield self.get_content() # Hook for the user
        yield Footer()

    def get_content(self):
        """
        Method to override by the user to insert his widgets
        if he wants to keep the default Header/Footer.
        """
        from textual.widgets import Label
        return Label("Override the `compose()` or `get_content()` method to display your widgets.")

    def action_toggle_dark(self) -> None:
        """Toggle between light and dark mode."""
        self.dark = not self.dark