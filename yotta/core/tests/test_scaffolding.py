import os
from pathlib import Path

from yotta.core.management.commands.startapp import (
    StartAppCommand,
    find_project_root,
    get_project_name,
)
from yotta.core.management.commands.startproject import StartProjectCommand

# ---------------------------------------------------------------------------
# startproject scaffolding
# ---------------------------------------------------------------------------


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

    assert "INSTALLED_APPS = [" in settings_py.read_text()
    assert "demo.main" in settings_py.read_text()
    assert f"YOTTA_SETTINGS_MODULE={settings_module}" in env_example.read_text()
    assert f'name = "{project_name}"' in pyproject.read_text()


def test_startproject_pyproject_uses_git_source_for_yotta(tmp_path):
    project_root = tmp_path / "demo"

    cmd = StartProjectCommand()
    cmd.create_structure(str(project_root), "demo", "settings", force=True)

    pyproject_content = (project_root / "pyproject.toml").read_text()

    assert 'dependencies = ["yotta"]' in pyproject_content
    assert "[tool.uv.sources]" in pyproject_content
    assert 'yotta = { git = "https://github.com/dim-gggl/yotta.git" }' in pyproject_content


def test_startproject_manage_py_has_no_leading_indentation(tmp_path):
    project_root = tmp_path / "demo"

    cmd = StartProjectCommand()
    cmd.create_structure(str(project_root), "demo", "settings", force=True)

    manage_py_content = (project_root / "manage.py").read_text()

    assert "\nimport os\n" in manage_py_content
    assert "\nimport sys\n" in manage_py_content
    assert "\n    import os\n" not in manage_py_content
    assert "\n    import sys\n" not in manage_py_content


# ---------------------------------------------------------------------------
# startapp scaffolding
# ---------------------------------------------------------------------------


def test_startapp_creates_app_files(tmp_path):
    package_root = tmp_path / "demo"
    package_root.mkdir()

    cmd = StartAppCommand()
    cmd.create_structure(str(package_root / "inventory"), "inventory", force=True)

    app_root = package_root / "inventory"
    assert (app_root / "__init__.py").exists()
    assert (app_root / "commands.py").exists()
    assert (app_root / "ui.py").exists()


# ---------------------------------------------------------------------------
# find_project_root
# ---------------------------------------------------------------------------


def _scaffold_project(root: Path, name: str = "demo") -> Path:
    """Helper: create a minimal yotta project structure at *root*."""
    StartProjectCommand().create_structure(str(root / name), name, "settings", force=True)
    return root / name


def test_find_project_root_from_project_root(tmp_path):
    project_root = _scaffold_project(tmp_path)
    result = find_project_root(start=str(project_root))
    assert result == project_root


def test_find_project_root_from_subdirectory(tmp_path):
    project_root = _scaffold_project(tmp_path)
    deep_dir = project_root / "demo" / "main"
    assert deep_dir.is_dir()
    result = find_project_root(start=str(deep_dir))
    assert result == project_root


def test_find_project_root_from_package_dir(tmp_path):
    project_root = _scaffold_project(tmp_path)
    result = find_project_root(start=str(project_root / "demo"))
    assert result == project_root


def test_find_project_root_returns_none_outside_project(tmp_path):
    (tmp_path / "random_file.txt").write_text("nothing here")
    result = find_project_root(start=str(tmp_path))
    assert result is None


def test_find_project_root_fallback_pyproject_and_settings(tmp_path):
    """Detect project root when manage.py is absent but pyproject.toml + settings.py exist."""
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "mypkg"\ndependencies = ["yotta"]\n')
    (tmp_path / "settings.py").write_text("INSTALLED_APPS = []\n")
    result = find_project_root(start=str(tmp_path))
    assert result == tmp_path


# ---------------------------------------------------------------------------
# get_project_name
# ---------------------------------------------------------------------------


def test_get_project_name_from_pyproject(tmp_path):
    project_root = _scaffold_project(tmp_path)
    assert get_project_name(project_root) == "demo"


def test_get_project_name_returns_none_when_no_pyproject(tmp_path):
    assert get_project_name(tmp_path) is None


def test_get_project_name_returns_none_for_malformed_toml(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool]\nkey = 42\n")
    assert get_project_name(tmp_path) is None


# ---------------------------------------------------------------------------
# StartAppCommand.run – integration with auto-detection
# ---------------------------------------------------------------------------


def test_run_autodetects_package_root(tmp_path, monkeypatch):
    """run() without --dst should scaffold inside <project_root>/<project_name>/."""
    project_root = _scaffold_project(tmp_path)
    monkeypatch.chdir(project_root)

    cmd = StartAppCommand()
    cmd.run("inventory", dst=None, force=True)

    app_dir = project_root / "demo" / "inventory"
    assert app_dir.is_dir()
    assert (app_dir / "__init__.py").exists()
    assert (app_dir / "commands.py").exists()


def test_run_autodetects_from_subdirectory(tmp_path, monkeypatch):
    """run() from a nested subdirectory should still find the project root."""
    project_root = _scaffold_project(tmp_path)
    deep_dir = project_root / "demo" / "main"
    monkeypatch.chdir(deep_dir)

    cmd = StartAppCommand()
    cmd.run("billing", dst=None, force=True)

    app_dir = project_root / "demo" / "billing"
    assert app_dir.is_dir()
    assert (app_dir / "commands.py").exists()


def test_run_with_explicit_dst(tmp_path):
    """run() with --dst should skip auto-detection entirely."""
    custom_dst = tmp_path / "custom_pkg"
    custom_dst.mkdir()

    cmd = StartAppCommand()
    cmd.run("shop", dst=str(custom_dst), force=True)

    assert (custom_dst / "shop" / "__init__.py").exists()


def test_run_fails_gracefully_outside_project(tmp_path, monkeypatch, capsys):
    """run() outside a yotta project prints a helpful error."""
    monkeypatch.chdir(tmp_path)

    cmd = StartAppCommand()
    cmd.run("oops", dst=None, force=False)

    app_dir = tmp_path / "oops"
    assert not app_dir.exists()
