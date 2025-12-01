import click
from functools import wraps
from yotta.core.context import Context

def command(name=None, **kwargs):
    """
    Wrapper around click.command that automatically injects 'ctx'.
    """
    def decorator(f):
        @click.command(name=name, **kwargs)
        @click.pass_context
        @wraps(f)
        def wrapper(click_ctx, *args, **kwargs):
            # Magic transformation: Click Context -> yotta Context
            yotta_ctx = Context(click_ctx)
            return f(yotta_ctx, *args, **kwargs)
        return wrapper
    return decorator

# The argument and option wrappers (New features)
# We pass them as is for now, but we could intercept them later
def argument(*args, **kwargs):
    return click.argument(*args, **kwargs)

def option(*args, **kwargs):
    return click.option(*args, **kwargs)
