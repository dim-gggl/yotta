import os
import sys

import pytest

from yotta.conf import Settings


def test_settings_loads_env_and_derives_module(tmp_path, monkeypatch):
    # Prepare a fake settings module
    settings_module = tmp_path / "settings_testenv.py"
    settings_module.write_text("INSTALLED_APPS = []\nVALUE = 'ok'\n")

    original_sys_path = list(sys.path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("YOTTA_SETTINGS_MODULE", raising=False)
    monkeypatch.setenv("YOTTA_ENV", "testenv")

    try:
        s = Settings()
        assert s.VALUE == "ok"
        assert s.INSTALLED_APPS == []
        assert os.environ["YOTTA_SETTINGS_MODULE"] == "settings_testenv"
    finally:
        sys.path[:] = original_sys_path


def test_settings_missing_module_raises(monkeypatch):
    monkeypatch.delenv("YOTTA_SETTINGS_MODULE", raising=False)
    monkeypatch.delenv("YOTTA_ENV", raising=False)
    s = Settings()
    with pytest.raises(ImportError):
        _ = s.NON_EXISTENT  # triggers _setup


def test_env_local_overrides_env_and_debug_flag(tmp_path, monkeypatch):
    settings_module = tmp_path / "settings.py"
    settings_module.write_text("INSTALLED_APPS = []\n")

    env_file = tmp_path / ".env"
    env_file.write_text("YOTTA_SETTINGS_MODULE=settings\nYOTTA_DEBUG=false\n")
    env_local = tmp_path / ".env.local"
    env_local.write_text("YOTTA_DEBUG=true\n")

    monkeypatch.chdir(tmp_path)
    s = Settings()
    assert s.debug_enabled is True


def test_settings_falls_back_to_global_defaults(tmp_path, monkeypatch):
    """When the project settings module omits an attribute, global_settings provides the default."""
    settings_file = tmp_path / "settings_fb.py"
    settings_file.write_text("INSTALLED_APPS = ['myapp']\n")

    original_sys_path = list(sys.path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("YOTTA_SETTINGS_MODULE", "settings_fb")

    try:
        s = Settings()
        assert s.INSTALLED_APPS == ["myapp"]
        assert s.THEME == "default"
        assert s.COMMAND_NAMESPACE == "none"
        assert s.COMMAND_NAMESPACE_SEPARATOR == ":"
    finally:
        sys.path[:] = original_sys_path


def test_settings_project_value_overrides_global_default(tmp_path, monkeypatch):
    """A value explicitly set in the project module takes precedence over global_settings."""
    settings_file = tmp_path / "settings_ov.py"
    settings_file.write_text('INSTALLED_APPS = []\nTHEME = "dark"\n')

    original_sys_path = list(sys.path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("YOTTA_SETTINGS_MODULE", "settings_ov")

    try:
        s = Settings()
        assert s.THEME == "dark"
    finally:
        sys.path[:] = original_sys_path


def test_settings_raises_for_truly_unknown_attribute(tmp_path, monkeypatch):
    """An attribute absent from both project settings and global_settings still raises."""
    settings_file = tmp_path / "settings_uk.py"
    settings_file.write_text("INSTALLED_APPS = []\n")

    original_sys_path = list(sys.path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("YOTTA_SETTINGS_MODULE", "settings_uk")

    try:
        s = Settings()
        with pytest.raises(AttributeError):
            _ = s.TOTALLY_NONEXISTENT_SETTING
    finally:
        sys.path[:] = original_sys_path
