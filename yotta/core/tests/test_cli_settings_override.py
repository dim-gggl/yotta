import os
import subprocess
import sys


def test_cli_settings_option_overrides_env_and_env_files(tmp_path):
    project_root = tmp_path / "proj"
    project_root.mkdir()

    # Project root marker for upward env search + sys.path insertion
    (project_root / "manage.py").write_text(
        """
import os
import sys
from yotta.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
""".lstrip(),
        encoding="utf-8",
    )

    pkg = project_root / "proj"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")

    # Two apps with two distinct commands
    app_a = pkg / "app_a"
    app_b = pkg / "app_b"
    app_a.mkdir()
    app_b.mkdir()
    (app_a / "__init__.py").write_text("", encoding="utf-8")
    (app_b / "__init__.py").write_text("", encoding="utf-8")

    (app_a / "commands.py").write_text(
        """
from yotta.cli.decorators import command
from yotta.core.context import YottaContext


@command(name="alpha", help="alpha command")
def alpha(yotta: YottaContext):
    yotta.ui.success("OK")
""".lstrip(),
        encoding="utf-8",
    )

    (app_b / "commands.py").write_text(
        """
from yotta.cli.decorators import command
from yotta.core.context import YottaContext


@command(name="beta", help="beta command")
def beta(yotta: YottaContext):
    yotta.ui.success("OK")
""".lstrip(),
        encoding="utf-8",
    )

    # Two different settings modules selecting different installed apps.
    (project_root / "settings_a.py").write_text(
        'INSTALLED_APPS = ["proj.app_a"]\n',
        encoding="utf-8",
    )
    (project_root / "settings_b.py").write_text(
        'INSTALLED_APPS = ["proj.app_b"]\n',
        encoding="utf-8",
    )

    # .env points to settings_b, but CLI --settings must override it.
    (project_root / ".env").write_text("YOTTA_SETTINGS_MODULE=settings_b\n", encoding="utf-8")

    env = os.environ.copy()
    env.pop("YOTTA_SETTINGS_MODULE", None)
    env["YOTTA_ENV"] = "ignored"

    result = subprocess.run(
        [sys.executable, "manage.py", "--settings=settings_a", "--help"],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "alpha command" in result.stdout
    assert "beta command" not in result.stdout






