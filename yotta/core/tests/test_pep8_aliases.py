def test_pep8_aliases_exist_and_are_compatible():
    from yotta.ui.console import YottaConsole, yottaConsole
    from yotta.ui.tui import YottaApp, yottaApp
    from yotta.core.management.utility import YottaUtility, yottaUtility

    assert YottaConsole is yottaConsole
    assert YottaApp is yottaApp
    assert YottaUtility is yottaUtility




