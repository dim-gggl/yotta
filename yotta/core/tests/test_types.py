import pytest
import click

from yotta.core import types
from enum import Enum


def test_email_type_accepts_valid_and_rejects_invalid():
    email_type = types.EMAIL
    assert email_type.convert("user@example.com", None, None) == "user@example.com"
    with pytest.raises(click.BadParameter):
        email_type.convert("invalid", None, None)


def test_file_type_extension_check(tmp_path):
    file_path = tmp_path / "data.csv"
    file_path.write_text("value")
    ftype = types.File(extension=".csv")
    assert ftype.convert(str(file_path), None, None)
    with pytest.raises(click.BadParameter):
        ftype_fail = types.File(extension=".json")
        ftype_fail.convert(str(file_path), None, None)


def test_directory_and_path_types(tmp_path):
    dir_type = types.Directory()
    path_type = types.Path()
    assert dir_type.convert(str(tmp_path), None, None) == str(tmp_path)

    file_path = tmp_path / "file.txt"
    file_path.write_text("ok")
    assert path_type.convert(str(file_path), None, None) == str(file_path)


def test_choice_helper_is_case_insensitive():
    choice = types.Choice(["red", "blue"], case_sensitive=False)
    assert choice.convert("RED", None, None) == "red"


def test_uuid_type():
    value = types.UUID().convert("12345678-1234-5678-1234-567812345678", None, None)
    assert str(value) == "12345678-1234-5678-1234-567812345678"
    with pytest.raises(click.BadParameter):
        types.UUID().convert("not-a-uuid", None, None)


def test_url_type():
    assert types.URL().convert("https://example.com", None, None) == "https://example.com"
    with pytest.raises(click.BadParameter):
        types.URL().convert("ftp://example.com", None, None)


def test_port_type():
    assert types.Port(1000, 2000).convert("1500", None, None) == 1500
    with pytest.raises(click.BadParameter):
        types.Port(1000, 2000).convert("900", None, None)


def test_json_type(tmp_path):
    obj = types.JSON().convert('{"a":1}', None, None)
    assert obj == {"a": 1}
    json_file = tmp_path / "data.json"
    json_file.write_text('{"b":2}')
    obj_file = types.JSON().convert(str(json_file), None, None)
    assert obj_file == {"b": 2}
    with pytest.raises(click.BadParameter):
        types.JSON().convert("not-json", None, None)


def test_enum_choice():
    class Color(Enum):
        RED = "red"
        BLUE = "blue"
    choice = types.EnumChoice(Color)
    assert choice.convert("red", None, None) == "red"
