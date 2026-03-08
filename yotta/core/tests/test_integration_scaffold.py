import os
import subprocess
import sys

import pytest

from yotta.conf import settings as settings_singleton
from yotta.core.management.commands.startapp import StartAppCommand
from yotta.core.management.commands.startcommand import StartCommandCommand
from yotta.core.management.commands.startproject import StartProjectCommand


@pytest.mark.integration
def test_scaffold_and_help(tmp_path, monkeypatch):
    project_root = tmp_path / "demo_project"
    project_name = "demo_project"
    settings_module = "settings"

    # Create project and app
    StartProjectCommand().create_structure(str(project_root), project_name, settings_module, force=True)
    StartAppCommand().create_structure(str(project_root / project_name / "inventory"), "inventory", force=True)

    # Make the scaffolded project importable so _resolve_commands_file works
    monkeypatch.syspath_prepend(str(project_root))

    # Add a command via startcommand
    start_cmd = StartCommandCommand()
    monkeypatch.setattr(start_cmd, "_select_app", lambda apps: f"{project_name}.inventory")
    monkeypatch.setattr(
        start_cmd,
        "_prompt_command_config",
        lambda: {
            "name": "demo",
            "function_name": "demo",
            "help": "demo command",
            "arguments": [],
            "options": [],
        },
    )
    start_cmd.run([], app=f"{project_name}.inventory")

    # Write a minimal manage.py compatible invocation
    env = os.environ.copy()
    env["YOTTA_SETTINGS_MODULE"] = settings_module
    # Simulate "python manage.py --help" by invoking the module
    result = subprocess.run(
        [sys.executable, "manage.py", "--help"],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "startproject" in result.stdout
    assert "startapp" in result.stdout
    assert "startcommand" in result.stdout


@pytest.mark.integration
def test_startcommand_from_nested_directory(tmp_path, monkeypatch):
    project_root = tmp_path / "my_cli"
    project_name = "my_cli"
    settings_module = "settings"

    StartProjectCommand().create_structure(str(project_root), project_name, settings_module, force=True)
    (project_root / ".env").write_text("YOTTA_SETTINGS_MODULE=settings\n", encoding="utf-8")

    nested_dir = project_root / project_name / "main"
    monkeypatch.chdir(nested_dir)
    monkeypatch.delenv("YOTTA_SETTINGS_MODULE", raising=False)
    monkeypatch.delenv("YOTTA_ENV", raising=False)
    settings_singleton._wrapped = None
    settings_singleton._env_loaded = False
    settings_singleton._sys_path_added = False
    sys.modules.pop("settings", None)
    sys.modules.pop(project_name, None)
    sys.modules.pop(f"{project_name}.main", None)

    start_cmd = StartCommandCommand()
    monkeypatch.setattr(start_cmd, "_select_app", lambda apps: f"{project_name}.main")
    monkeypatch.setattr(
        start_cmd,
        "_prompt_command_config",
        lambda: {
            "name": "nested-demo",
            "function_name": "nested_demo",
            "help": "demo command from nested dir",
            "arguments": [],
            "options": [],
        },
    )

    start_cmd.run([], app=None)

    commands_py = project_root / project_name / "main" / "commands.py"
    assert "nested_demo" in commands_py.read_text(encoding="utf-8")
