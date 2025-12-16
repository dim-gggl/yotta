import importlib
import types

import click
import pytest

from yotta.conf import settings
from yotta.core.loader import AppLoader


def test_loader_warns_when_commands_module_missing(monkeypatch, capsys):
    monkeypatch.setattr(settings, "INSTALLED_APPS", ["myapp"], raising=False)

    def fake_import(name):
        raise ImportError(f"No module named '{name}'")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    loader = AppLoader()
    commands = loader.get_commands()

    assert commands == {}
    out = capsys.readouterr().out
    assert "No commands.py found for app 'myapp'" in out


def test_loader_raises_non_missing_import_error(monkeypatch):
    monkeypatch.setattr(settings, "INSTALLED_APPS", ["badapp"], raising=False)

    def fake_import(name):
        raise ImportError("crash")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    loader = AppLoader(strict=True)
    with pytest.raises(ImportError):
        loader.get_commands()


def test_loader_collects_commands(monkeypatch):
    monkeypatch.setattr(settings, "INSTALLED_APPS", ["demo"], raising=False)

    cmd = click.command(name="hello")(lambda: None)
    module = types.SimpleNamespace(hello=cmd)

    def fake_import(name):
        if name.endswith(".commands"):
            return module
        raise ImportError(f"No module named '{name}'")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    loader = AppLoader()
    commands = loader.get_commands()

    assert "hello" in commands
    assert commands["hello"] is cmd
