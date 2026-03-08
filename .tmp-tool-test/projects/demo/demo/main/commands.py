
from yotta.cli.decorators import command
from yotta.core.context import YottaContext


@command(name="hello")
def hello_world(yotta: YottaContext):
    """Simple example command shipped with your new project."""
    yotta.ui.header("Hello from yotta")
    yotta.ui.success("Your project is ready. Edit this command to get started!")
