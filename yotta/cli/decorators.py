from functools import wraps
from typing import Any

import rich_click as click

from yotta.core import types as ytypes
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
            yotta_ctx = YottaContext(click_ctx)
            return f(yotta_ctx, *args, **kwargs)

        return wrapper

    return decorator


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


_TYPE_ALIAS_MAP: dict[str, Any] = {
    "email": ytypes.EMAIL,
    "int": click.INT,
    "float": click.FLOAT,
    "str": click.STRING,
    "string": click.STRING,
    "path": ytypes.PATH,
    "filepath": ytypes.PATH,
    "dir": ytypes.DIRECTORY,
    "directory": ytypes.DIRECTORY,
    "uuid": ytypes.UUID_TYPE,
    "url": ytypes.URL_TYPE,
    "json": ytypes.JSON_TYPE,
    "port": ytypes.PORT,
}


def _resolve_type_alias(type_hint: Any) -> Any:
    """
    Translate short string aliases to yotta core types to keep decorators ergonomic.
    """
    if not isinstance(type_hint, str):
        return type_hint
    return _TYPE_ALIAS_MAP.get(type_hint.lower().strip(), type_hint)
