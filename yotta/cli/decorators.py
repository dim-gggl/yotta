import rich_click as click
from functools import wraps
from typing import Any

from yotta.core.context import YottaContext

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
            yotta_ctx = YottaContext(click_ctx)
            return f(yotta_ctx, *args, **kwargs)
        return wrapper
    return decorator

# The argument and option wrappers (New features)

def argument(*args, **kwargs):
    """
    Thin wrapper that resolves known yotta type aliases (e.g. \"email\") before delegating to Click.
    """
    if "type" in kwargs:
        kwargs["type"] = _resolve_type_alias(kwargs["type"])
    return click.argument(*args, **kwargs)


def option(*args, **kwargs):
    """
    Wrapper over click.option that:
    - Resolves string type aliases to yotta/core/types.
    - Automatically enables show_default when a default is provided and no value was supplied.
    """
    if "type" in kwargs:
        kwargs["type"] = _resolve_type_alias(kwargs["type"])

    if "show_default" not in kwargs and "default" in kwargs and not kwargs.get("is_flag"):
        kwargs["show_default"] = True

    return click.option(*args, **kwargs)


def _resolve_type_alias(type_hint: Any):
    """
    Translate short string aliases to yotta core types to keep decorators ergonomic.
    """
    if not isinstance(type_hint, str):
        return type_hint

    alias = type_hint.lower().strip()
    if alias == "email":
        from yotta.core import types as ytypes
        return ytypes.EMAIL
    if alias == "int":
        return click.INT
    if alias == "float":
        return click.FLOAT
    if alias in ("str", "string"):
        return click.STRING
    if alias in ("path", "filepath"):
        from yotta.core import types as ytypes
        return ytypes.PATH
    if alias in ("dir", "directory"):
        from yotta.core import types as ytypes
        return ytypes.DIRECTORY
    if alias == "uuid":
        from yotta.core import types as ytypes
        return ytypes.UUID_TYPE
    if alias == "url":
        from yotta.core import types as ytypes
        return ytypes.URL
    if alias == "json":
        from yotta.core import types as ytypes
        return ytypes.JSON
    if alias == "port":
        from yotta.core import types as ytypes
        return ytypes.PORT

    # Unknown alias, leave untouched so Click can handle or error
    return type_hint
