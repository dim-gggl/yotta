import types

import pytest
from rich.console import Console

import yotta.conf
from yotta.core.management.commands.startcommand import StartCommandCommand


def test_startcommand_helpers_are_class_methods() -> None:
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
        "_is_valid_cli_name",
    ]
    for name in required_helpers:
        assert hasattr(StartCommandCommand, name), f"Missing StartCommandCommand.{name}"


def test_startcommand_run_appends_command_block(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        yotta.conf,
        "settings",
        types.SimpleNamespace(INSTALLED_APPS=["demo.main"]),
    )

    commands_file = tmp_path / "commands.py"

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


# ---------------------------------------------------------------------------
# _to_identifier – sanitisation
# ---------------------------------------------------------------------------


class TestToIdentifier:
    """Verify that _to_identifier produces valid Python identifiers."""

    cmd = StartCommandCommand()

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("hello", "hello"),
            ("hello world", "hello_world"),
            ("hello-world", "hello_world"),
            ("my_cmd", "my_cmd"),
        ],
    )
    def test_normal_names(self, raw: str, expected: str) -> None:
        assert self.cmd._to_identifier(raw) == expected

    def test_leading_digit_gets_underscore_prefix(self) -> None:
        assert self.cmd._to_identifier("1abc") == "_1abc"
        assert self.cmd._to_identifier("42") == "_42"

    @pytest.mark.parametrize("kw", ["class", "return", "import", "for", "if"])
    def test_python_keywords_get_underscore_suffix(self, kw: str) -> None:
        result = self.cmd._to_identifier(kw)
        assert result == f"{kw}_"
        assert result.isidentifier()

    def test_special_characters_stripped(self) -> None:
        assert self.cmd._to_identifier("foo/bar") == "foobar"
        assert self.cmd._to_identifier("a@b!c") == "abc"
        assert self.cmd._to_identifier("hello world!") == "hello_world"

    def test_all_special_returns_empty(self) -> None:
        assert self.cmd._to_identifier("///") == ""
        assert self.cmd._to_identifier("@#$") == ""

    def test_leading_digit_plus_special(self) -> None:
        result = self.cmd._to_identifier("1foo/bar")
        assert result == "_1foobar"
        assert result.isidentifier()

    def test_whitespace_only_returns_empty(self) -> None:
        assert self.cmd._to_identifier("   ") == ""

    def test_result_always_valid_when_non_empty(self) -> None:
        cases = ["ok", "hello world", "1abc", "class", "foo-bar", "a/b"]
        for raw in cases:
            result = self.cmd._to_identifier(raw)
            assert result.isidentifier(), f"_to_identifier({raw!r}) → {result!r} is not a valid identifier"
            assert not __import__("keyword").iskeyword(result), f"_to_identifier({raw!r}) → {result!r} is a keyword"


# ---------------------------------------------------------------------------
# _is_valid_cli_name
# ---------------------------------------------------------------------------


class TestIsValidCliName:
    cmd = StartCommandCommand()

    @pytest.mark.parametrize(
        "name",
        [
            "hello",
            "hello-world",
            "hello_world",
            "_test",
            "run2",
        ],
    )
    def test_valid_names(self, name: str) -> None:
        assert self.cmd._is_valid_cli_name(name)

    @pytest.mark.parametrize(
        "name",
        [
            "1abc",
            "foo/bar",
            "",
            "foo bar",
            "-flag",
            "hello!",
        ],
    )
    def test_invalid_names(self, name: str) -> None:
        assert not self.cmd._is_valid_cli_name(name)
