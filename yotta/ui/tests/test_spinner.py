from rich.align import Align
import pytest

from yotta.ui.spinner import centered_spinner, spinner
from yotta.ui.theme import resolve_theme
from yotta.conf import settings


@pytest.fixture(autouse=True)
def _ensure_settings_env(monkeypatch):
    monkeypatch.setenv("YOTTA_SETTINGS_MODULE", "yotta.conf.global_settings")


def test_spinner_is_valid_context_manager():
    with spinner("Working..."):
        pass


def test_centered_spinner_returns_renderable():
    renderable = centered_spinner("Working...")
    assert isinstance(renderable, Align)


def test_spinner_uses_active_theme(monkeypatch):
    monkeypatch.setattr(settings, "THEME", "dark", raising=False)

    sp = spinner("Working...")

    theme = resolve_theme("dark")
    assert sp.renderable.style == theme.styles["primary"]
