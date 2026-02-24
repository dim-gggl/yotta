from click.testing import CliRunner

from yotta.core.management.commands.completion import _complete_var
from yotta.core.management.utility import YottaUtility


def test_complete_var_derives_env_var_from_command():
    assert _complete_var("yotta") == "_YOTTA_COMPLETE"
    assert _complete_var("python manage.py") == "_MANAGE_PY_COMPLETE"
    assert _complete_var("my-cli") == "_MY_CLI_COMPLETE"


def test_completion_command_outputs_shell_snippet_for_zsh():
    runner = CliRunner()
    cli = YottaUtility(argv=["manage.py"]).build_cli()
    result = runner.invoke(cli, ["completion", "--shell", "zsh", "--command", "python manage.py"])

    assert result.exit_code == 0
    assert "_MANAGE_PY_COMPLETE=zsh_source" in result.output
    assert "python manage.py" in result.output


def test_completion_command_outputs_shell_snippet_for_fish():
    runner = CliRunner()
    cli = YottaUtility(argv=["manage.py"]).build_cli()
    result = runner.invoke(cli, ["completion", "--shell", "fish", "--command", "yotta"])

    assert result.exit_code == 0
    assert "_YOTTA_COMPLETE=fish_source" in result.output
    assert "yotta" in result.output


def test_completion_default_command_is_yotta():
    runner = CliRunner()
    cli = YottaUtility(argv=["yotta"]).build_cli()
    result = runner.invoke(cli, ["completion", "--shell", "bash"])

    assert result.exit_code == 0
    assert "_YOTTA_COMPLETE=bash_source" in result.output
    assert "yotta" in result.output
