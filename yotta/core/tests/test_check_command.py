import sys

import rich_click as click
from click.testing import CliRunner

from yotta.conf import settings as settings_singleton
from yotta.core.management.commands.check import check_command


def _reset_settings_singleton() -> None:
    # Make diagnostics deterministic for tests by clearing the cached module/env.
    settings_singleton._wrapped = None
    settings_singleton._env_loaded = False
    settings_singleton._sys_path_added = False
    settings_singleton._project_root = None
    settings_singleton._env_files_loaded = []
    settings_singleton._env_loaded_values = {}


def test_check_command_reports_ok_for_minimal_project(tmp_path, monkeypatch):
    # Minimal project root markers
    (tmp_path / "manage.py").write_text("# marker\n", encoding="utf-8")

    # Minimal settings module
    settings_name = "settings_check_ok"
    (tmp_path / f"{settings_name}.py").write_text("INSTALLED_APPS = []\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("YOTTA_SETTINGS_MODULE", settings_name)
    sys.modules.pop(settings_name, None)
    _reset_settings_singleton()

    runner = CliRunner()
    result = runner.invoke(check_command, [])

    assert result.exit_code == 0
    assert "yotta check" in result.output
    assert "Status" in result.output


def test_check_command_fails_when_settings_missing(monkeypatch):
    monkeypatch.delenv("YOTTA_SETTINGS_MODULE", raising=False)
    monkeypatch.delenv("YOTTA_ENV", raising=False)
    _reset_settings_singleton()

    runner = CliRunner()
    result = runner.invoke(check_command, [])

    assert result.exit_code != 0
    assert "Settings failed to load" in result.output


def test_check_command_detects_missing_commands_module_in_strict_mode(tmp_path, monkeypatch):
    (tmp_path / "manage.py").write_text("# marker\n", encoding="utf-8")

    # Create a tiny package app with no commands.py
    pkg_root = tmp_path / "demo"
    pkg_root.mkdir()
    (pkg_root / "__init__.py").write_text("", encoding="utf-8")

    settings_name = "settings_check_strict"
    (tmp_path / f"{settings_name}.py").write_text('INSTALLED_APPS = ["demo"]\n', encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("YOTTA_SETTINGS_MODULE", settings_name)
    sys.modules.pop(settings_name, None)
    _reset_settings_singleton()

    runner = CliRunner()

    @click.group()
    @click.option("--quiet", is_flag=True)
    @click.option("--verbose", is_flag=True)
    @click.option("--strict", is_flag=True)
    def root(quiet, verbose, strict):
        pass

    root.add_command(check_command, name="check")

    result = runner.invoke(root, ["--strict", "check"])
    assert result.exit_code == 1
    assert "Missing commands module" in result.output or "no commands.py" in result.output
