import click
import pytest
from click.testing import CliRunner

from yotta.cli.decorators import argument, command, option
from yotta.core import types as ytypes


def test_command_injects_yotta_context_and_runs():
    invoked = {}

    @command(name="greet")
    @argument("name")
    def greet_cmd(yotta_ctx, name):
        # Ensure yotta context is injected and has ui
        invoked["ui_exists"] = hasattr(yotta_ctx, "ui")
        invoked["name"] = name

    runner = CliRunner()
    result = runner.invoke(greet_cmd, ["alice"])

    assert result.exit_code == 0
    assert invoked["ui_exists"] is True
    assert invoked["name"] == "alice"


def test_argument_and_option_resolve_type_aliases(tmp_path):
    @command(name="paths")
    @argument("email", type="email")
    @option("--src", type="path", default=str(tmp_path))
    @option("--dst", type="directory", default=str(tmp_path))
    def paths_cmd(yotta_ctx, email, src, dst):
        yotta_ctx.ui  # accessed to ensure context exists

    params = {param.name: param for param in paths_cmd.params}

    assert isinstance(params["email"].type, type(ytypes.EMAIL))
    assert isinstance(params["src"].type, type(ytypes.PATH))
    assert params["src"].show_default is True
    assert isinstance(params["dst"].type, type(ytypes.DIRECTORY))


def test_option_auto_show_default_for_non_flags(tmp_path):
    @command(name="opt")
    @option("--file", default="value.txt")
    def opt_cmd(yotta_ctx, file):
        pass

    file_param = next(p for p in opt_cmd.params if p.name == "file")
    assert file_param.show_default is True
