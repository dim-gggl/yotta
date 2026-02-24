from typing import Any

from rich.align import Align
from rich.console import Console, RenderableType
from rich.spinner import Spinner

from yotta.conf import settings
from yotta.ui.theme import resolve_theme


class YottaSpinner:
    def __init__(self, message: RenderableType = "Loading...", spinner_name: str = "dots12") -> None:
        theme_name = getattr(settings, "THEME", "default")
        theme = resolve_theme(theme_name)
        self.renderable = Spinner(spinner_name, message, style=theme.styles["primary"])
        self._status: Any = None

    def __enter__(self) -> "YottaSpinner":
        self._status = Console(stderr=True).status(self.renderable)
        self._status.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self._status:
            self._status.__exit__(exc_type, exc_value, traceback)
            self._status = None

    def centered(self) -> Align:
        return Align.center(self.renderable)


yottaSpinner = YottaSpinner  # deprecated alias


def spinner(message: RenderableType = "Loading...", spinner_name: str = "dots12") -> YottaSpinner:
    return YottaSpinner(message, spinner_name)


def centered_spinner(message: RenderableType = "Loading...", spinner_name: str = "dots12") -> Align:
    return YottaSpinner(message, spinner_name).centered()
