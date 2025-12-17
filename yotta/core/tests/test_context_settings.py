from types import SimpleNamespace

from yotta.conf import settings as settings_singleton
from yotta.core.context import YottaContext


def test_yotta_context_exposes_settings_singleton_lazily() -> None:
    ctx = YottaContext(SimpleNamespace(obj=None))

    # This should not be None and should be the singleton proxy object.
    assert ctx.settings is settings_singleton


