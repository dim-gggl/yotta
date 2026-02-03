from click.testing import CliRunner

from yotta.core.management.utility import YottaUtility


def test_root_cli_supports_version_option():
    runner = CliRunner()
    cli = YottaUtility(argv=["manage.py"]).build_cli()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert result.output.strip().startswith("yotta ")
