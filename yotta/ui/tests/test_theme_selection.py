from types import SimpleNamespace

import yotta.conf
from yotta.ui.console import yottaConsole
from yotta.ui.theme import DEFAULT_THEME, DARK_THEME


def test_console_uses_theme_from_settings(monkeypatch) -> None:
    monkeypatch.setattr(yotta.conf, "settings", SimpleNamespace(THEME="dark"))
    ui = yottaConsole()
    assert ui.theme is DARK_THEME
    assert ui.theme_name.lower() == "dark"


def test_console_unknown_theme_falls_back_to_default(monkeypatch) -> None:
    monkeypatch.setattr(yotta.conf, "settings", SimpleNamespace(THEME="does-not-exist"))
    ui = yottaConsole()
    assert ui.theme is DEFAULT_THEME


def test_console_settings_unavailable_falls_back_to_default(monkeypatch) -> None:
    class ExplodingSettings:
        def __getattr__(self, name: str):
            raise RuntimeError("settings unavailable")

    monkeypatch.setattr(yotta.conf, "settings", ExplodingSettings())
    ui = yottaConsole()
    assert ui.theme is DEFAULT_THEME


def test_console_explicit_theme_overrides_settings(monkeypatch) -> None:
    monkeypatch.setattr(yotta.conf, "settings", SimpleNamespace(THEME="default"))
    ui = yottaConsole(theme="dark")
    assert ui.theme is DARK_THEME


