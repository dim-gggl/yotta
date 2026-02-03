def test_cli_types_module_reexports_core_types():
    from yotta.cli.types import EMAIL, PATH, DIRECTORY, UUID_TYPE, URL_TYPE, JSON_TYPE, PORT
    from yotta.core import types as ytypes

    assert EMAIL is ytypes.EMAIL
    assert PATH is ytypes.PATH
    assert DIRECTORY is ytypes.DIRECTORY
    assert UUID_TYPE is ytypes.UUID_TYPE
    assert URL_TYPE is ytypes.URL_TYPE
    assert JSON_TYPE is ytypes.JSON_TYPE
    assert PORT is ytypes.PORT
