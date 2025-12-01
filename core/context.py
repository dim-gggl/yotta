import click
# We import our new class
try:
    from yotta.ui.console import yottaConsole
except ImportError:
    yottaConsole = None  # Fallback or warning could go here


class Context:
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
