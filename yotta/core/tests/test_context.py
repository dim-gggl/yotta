from types import SimpleNamespace

from yotta.conf import settings as settings_singleton
from yotta.core.context import YottaContext


def test_context_exposes_settings_singleton_lazily() -> None:
    ctx = YottaContext(SimpleNamespace(obj=None))
    assert ctx.settings is settings_singleton
    # Cached on the context instance
    assert ctx.settings is settings_singleton


