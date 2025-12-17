import types

from rich.console import Console

import yotta.conf
from yotta.core.management.commands.startcommand import StartCommandCommand


def test_startcommand_helpers_are_class_methods() -> None:
    # Regression test: helpers must be defined on the class, not nested inside the click entrypoint.
    required_helpers = [
        "_select_app",
        "_resolve_commands_file",
        "_prompt_command_config",
        "_render_command_block",
        "_command_decorator",
        "_option_decorator",
        "_prompt_identifier",
        "_prompt_required",
        "_confirm",
        "_escape_quotes",
        "_base_commands_file",
        "_ensure_imports",
        "_write_file",
        "_to_identifier",
    ]
    for name in required_helpers:
        assert hasattr(StartCommandCommand, name), f"Missing StartCommandCommand.{name}"


def test_startcommand_run_appends_command_block(tmp_path, monkeypatch) -> None:
    # Provide fake settings without touching the real settings loader.
    monkeypatch.setattr(
        yotta.conf,
        "settings",
        types.SimpleNamespace(INSTALLED_APPS=["demo.main"]),
    )

    commands_file = tmp_path / "commands.py"

    # Ensure these helpers exist (raising=True by default) and drive the run() flow without interactive prompts.
    monkeypatch.setattr(StartCommandCommand, "_select_app", lambda self, apps: "demo.main")
    monkeypatch.setattr(StartCommandCommand, "_resolve_commands_file", lambda self, app_path: str(commands_file))
    monkeypatch.setattr(
        StartCommandCommand,
        "_prompt_command_config",
        lambda self: {"name": "mycmd", "function_name": "mycmd", "help": "", "arguments": [], "options": []},
    )
    monkeypatch.setattr(StartCommandCommand, "_render_command_block", lambda self, cfg: "\n\n# BLOCK\n")

    cmd = StartCommandCommand()
    cmd.console = Console(record=True)
    cmd.run([], app=None)

    content = commands_file.read_text(encoding="utf-8")
    assert "from yotta.cli.decorators import command, argument, option" in content
    assert "from yotta.core.context import YottaContext" in content
    assert "# BLOCK" in content
    assert "Added" in cmd.console.export_text()


def test_startcommand_run_cancelled_when_no_app_selected(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        yotta.conf,
        "settings",
        types.SimpleNamespace(INSTALLED_APPS=["demo.main"]),
    )

    commands_file = tmp_path / "commands.py"

    monkeypatch.setattr(StartCommandCommand, "_select_app", lambda self, apps: None)
    monkeypatch.setattr(StartCommandCommand, "_resolve_commands_file", lambda self, app_path: str(commands_file))

    cmd = StartCommandCommand()
    cmd.console = Console(record=True)
    cmd.run([], app=None)

    assert not commands_file.exists()
    assert "No app selected. Nothing was created." in cmd.console.export_text()


