import rich_click as click
from yotta.ui.console import yottaConsole


class YottaContext:
    """
    The yotta context that travels from command to command.
    It contains the settings and the UI engine.
    """
    def __init__(self, click_ctx):
        self.click_ctx = click_ctx
        # Instantiation of the complete UI engine
        self.ui = yottaConsole()

        # (Placeholder for future settings)
        self.settings = None
