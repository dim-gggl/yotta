from importlib.metadata import PackageNotFoundError

from click.testing import CliRunner

from yotta.core.management import utility
from yotta.core.management.utility import YottaUtility


def test_root_cli_supports_version_option():
    runner = CliRunner()
    cli = YottaUtility(argv=["manage.py"]).build_cli()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip().startswith("yotta ")


def test_root_cli_falls_back_to_yotta_framework_distribution(monkeypatch):
    def fake_pkg_version(name: str) -> str:
        if name == "yotta":
            raise PackageNotFoundError(name)
        if name == "yotta-framework":
            return "1.0"
        raise AssertionError(f"Unexpected package lookup: {name}")

    monkeypatch.setattr(utility, "_pkg_version", fake_pkg_version)

    runner = CliRunner()
    cli = YottaUtility(argv=["manage.py"]).build_cli()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip() == "yotta 1.0"
