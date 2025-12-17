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

        # Settings are exposed lazily to avoid triggering imports / file IO
        # unless the command actually needs configuration.
        self._settings = None

    @property
    def settings(self):
        """
        Lazily expose the settings singleton.

        This returns `yotta.conf.settings` (a proxy that loads the configured module
        only when its attributes are accessed).
        """
        if self._settings is None:
            from yotta.conf import settings as settings_singleton

            self._settings = settings_singleton
        return self._settings
