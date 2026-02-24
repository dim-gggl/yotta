from rich.align import Align
from rich.console import Console
from rich.spinner import Spinner

from yotta.conf import settings
from yotta.ui.theme import resolve_theme


class yottaSpinner:
    def __init__(self, message: str = "Loading...", spinner_name: str = "dots12"):
        theme_name = getattr(settings, "THEME", "default")
        theme = resolve_theme(theme_name)
        self.renderable = Spinner(spinner_name, message, style=theme.styles["primary"])
        self._status = None

    def __enter__(self):
        self._status = Console(stderr=True).status(self.renderable)
        self._status.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._status:
            self._status.__exit__(exc_type, exc_value, traceback)
            self._status = None

    def centered(self):
        return Align.center(self.renderable)


def spinner(message: str = "Loading...", spinner_name: str = "dots12"):
    return yottaSpinner(message, spinner_name)


def centered_spinner(message: str = "Loading...", spinner_name: str = "dots12"):
    return yottaSpinner(message, spinner_name).centered()
