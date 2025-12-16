import os

from yotta.core.management.commands.startproject import StartProjectCommand
from yotta.core.management.commands.startapp import StartAppCommand


def test_startproject_creates_structure(tmp_path):
    base_dir = tmp_path
    project_name = "demo"
    settings_module = "settings_local"

    cmd = StartProjectCommand()
    cmd.create_structure(str(base_dir / project_name), project_name, settings_module, force=True)

    project_root = base_dir / project_name
    manage_py = project_root / "manage.py"
    settings_py = project_root / "settings.py"
    pyproject = project_root / "pyproject.toml"
    env_example = project_root / ".env.example"
    commands_py = project_root / project_name / "main" / "commands.py"

    assert manage_py.exists()
    assert os.access(manage_py, os.X_OK)
    assert settings_py.exists()
    assert pyproject.exists()
    assert env_example.exists()
    assert commands_py.exists()

    assert 'INSTALLED_APPS = [' in settings_py.read_text()
    assert 'demo.main' in settings_py.read_text()
    assert f"YOTTA_SETTINGS_MODULE={settings_module}" in env_example.read_text()
    assert f'name = "{project_name}"' in pyproject.read_text()


def test_startapp_creates_app_files(tmp_path):
    package_root = tmp_path / "demo"
    package_root.mkdir()

    cmd = StartAppCommand()
    cmd.create_structure(str(package_root / "inventory"), "inventory", force=True)

    app_root = package_root / "inventory"
    assert (app_root / "__init__.py").exists()
    assert (app_root / "commands.py").exists()
    assert (app_root / "ui.py").exists()
