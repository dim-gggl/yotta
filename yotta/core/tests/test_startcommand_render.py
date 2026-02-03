from yotta.core.management.commands.startcommand import StartCommandCommand


def test_render_command_block_includes_typed_arguments_and_options() -> None:
    cmd = StartCommandCommand()
    config = {
        "name": "demo",
        "function_name": "demo",
        "help": "demo command",
        "arguments": [
            {"name": "email", "param": "email", "type": "email", "help": "User email"},
            {"name": "count", "param": "count", "type": "int", "help": ""},
        ],
        "options": [
            {
                "name": "limit",
                "param": "limit",
                "short": "l",
                "is_flag": False,
                "default": "10",
                "required": False,
                "type": "int",
                "help": "Limit results",
            },
            {
                "name": "force",
                "param": "force",
                "short": "f",
                "is_flag": True,
                "default": None,
                "required": False,
                "type": None,
                "help": "Force it",
            },
            {
                "name": "name",
                "param": "name",
                "short": None,
                "is_flag": False,
                "default": None,
                "required": True,
                "type": "string",
                "help": "",
            },
        ],
    }

    block = cmd._render_command_block(config)

    assert '@argument("email", type="email", help="User email")' in block
    assert '@argument("count", type="int")' in block
    assert '@option("-l", "--limit", type="int", default=10, show_default=True, help="Limit results")' in block
    assert '@option("-f", "--force", is_flag=True, default=False, help="Force it")' in block
    assert '@option("--name", type="string", required=True)' in block


def test_format_default_literal_int_and_float() -> None:
    cmd = StartCommandCommand()
    assert cmd._format_default_literal("42", "int") == "42"
    assert cmd._format_default_literal("42", "port") == "42"
    assert cmd._format_default_literal("3.5", "float") == "3.5"
    assert cmd._format_default_literal("x", "int") == repr("x")

