from rich.spinner import Spinner
from rich.align import Align
from yotta.ui.theme import DEFAULT_THEME


class yottaSpinner:

    def __init__(self, message: str = "Loading...", spinner: str = "dots12"):
        self.spinner = Spinner(spinner, message, style=DEFAULT_THEME.styles["primary"])

    def __enter__(self):
        return self.centered().start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.align.stop()
    
    def centered(self):
        return Align.center(self.spinner)


def spinner(message: str = "Loading...", spinner: str = "dots12"):
    return yottaSpinner(message, spinner)

def centered_spinner(message: str = "Loading...", spinner: str = "dots12"):
    return yottaSpinner(message, spinner).centered()
