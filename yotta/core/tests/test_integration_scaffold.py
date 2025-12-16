import os
import subprocess
import sys
from pathlib import Path

import pytest

from yotta.core.management.commands.startproject import StartProjectCommand
from yotta.core.management.commands.startapp import StartAppCommand
from yotta.core.management.commands.startcommand import StartCommandCommand


@pytest.mark.integration
def test_scaffold_and_help(tmp_path, monkeypatch):
    project_root = tmp_path / "demo_project"
    project_name = "demo_project"
    settings_module = "settings"

    # Create project and app
    StartProjectCommand().create_structure(str(project_root), project_name, settings_module, force=True)
    StartAppCommand().create_structure(str(project_root / project_name / "inventory"), "inventory", force=True)

    # Add a command via startcommand
    start_cmd = StartCommandCommand()
    # Mock prompt selections
    monkeypatch.setattr(start_cmd, "_select_app", lambda apps: f"{project_name}.inventory")
    monkeypatch.setattr(start_cmd, "_prompt_command_config", lambda: {
        "name": "demo",
        "function_name": "demo",
        "help": "demo command",
        "arguments": [],
        "options": [],
    })
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
