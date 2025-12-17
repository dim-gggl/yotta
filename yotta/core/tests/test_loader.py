import importlib
import types

import click
import pytest

from yotta.conf import settings
from yotta.core.loader import AppLoader, DuplicateCommandNameError


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


def test_loader_warns_on_duplicate_command_names_and_keeps_last(monkeypatch, capsys):
    monkeypatch.setattr(settings, "INSTALLED_APPS", ["app1", "app2"], raising=False)

    cmd1 = click.command(name="hello")(lambda: None)
    cmd2 = click.command(name="hello")(lambda: None)
    module1 = types.SimpleNamespace(hello=cmd1)
    module2 = types.SimpleNamespace(hello=cmd2)

    def fake_import(name):
        if name == "app1.commands":
            return module1
        if name == "app2.commands":
            return module2
        raise ImportError(f"No module named '{name}'")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    loader = AppLoader()
    commands = loader.get_commands()

    assert commands["hello"] is cmd2  # last wins
    out = capsys.readouterr().out
    assert "Duplicate command name 'hello'" in out
    assert "app1.commands:hello" in out
    assert "app2.commands:hello" in out


def test_loader_raises_on_duplicate_command_names_in_strict_mode(monkeypatch):
    monkeypatch.setattr(settings, "INSTALLED_APPS", ["app1", "app2"], raising=False)

    cmd1 = click.command(name="hello")(lambda: None)
    cmd2 = click.command(name="hello")(lambda: None)
    module1 = types.SimpleNamespace(hello=cmd1)
    module2 = types.SimpleNamespace(hello=cmd2)

    def fake_import(name):
        if name == "app1.commands":
            return module1
        if name == "app2.commands":
            return module2
        raise ImportError(f"No module named '{name}'")

    monkeypatch.setattr(importlib, "import_module", fake_import)

    loader = AppLoader(strict=True)
    with pytest.raises(DuplicateCommandNameError):
        loader.get_commands()
