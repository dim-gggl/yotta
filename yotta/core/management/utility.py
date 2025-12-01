import sys
import os
import rich_click as click
from yotta.core.management.commands.startproject import StartProjectCommand
from yotta.core.management.commands.startapp import StartAppCommand


class yottaUtility:
    def __init__(self, argv=None):
        self.argv = argv or sys.argv[:]

    def execute(self):
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = None

        # 1. Management of system commands (Bootstrap)
        if subcommand == 'startproject':
            StartProjectCommand().run(self.argv[2:])
            return

        if subcommand == 'startapp':
            StartAppCommand().run(self.argv[2:])
            return

        # 2. Management of user commands (Runtime)
        # Here the magic happens: we create a dynamic Click group
        
        # We need to ensure that settings is accessible before loading the loader
        if "YOTTA_SETTINGS_MODULE" not in os.environ:
             # Fallback simple for development, but manage.py already does this
             pass

        from yotta.core.loader import AppLoader
        
        loader = AppLoader()
        discovered_commands = loader.get_commands()

        # We create a root Click Group that contains all the discovered commands
        @click.group()
        def cli():
            pass

        # We attach each discovered command to the root group
        for name, cmd in discovered_commands.items():
            cli.add_command(cmd, name=name)

        # We launch Click (it will parse sys.argv automatically)
        try:
            # prog_name allows to display 'manage.py' in the help instead of the python script
            cli(prog_name="manage.py")
        except Exception as e:
            # Here we could add a nice error handler with Rich
            raise e

def execute_from_command_line(argv=None):
    utility = yottaUtility(argv)
    utility.execute()