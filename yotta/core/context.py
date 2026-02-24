from collections.abc import Callable
from typing import Any

from yotta.conf import settings as _settings_singleton
from yotta.ui.console import YottaConsole

# Default UI factory — can be overridden for testing or alternative UI backends.
_default_ui_factory: Callable[[], Any] = YottaConsole


class YottaContext:
    """
    The yotta context that travels from command to command.
    It contains the settings and the UI engine.

    The UI is injected via *ui_factory* so that ``core`` depends on a callable
    rather than a concrete class, keeping the layer boundary explicit.
    """

    def __init__(self, click_ctx, ui_factory: Callable[[], Any] | None = None) -> None:
        self.click_ctx = click_ctx
        self.ui = (ui_factory or _default_ui_factory)()
        self._settings = None

    @property
    def settings(self):
        """
        Lazily expose the settings singleton.

        This returns `yotta.conf.settings` (a proxy that loads the configured module
        only when its attributes are accessed).
        """
        if not self._settings:
            self._settings = _settings_singleton
        return self._settings
