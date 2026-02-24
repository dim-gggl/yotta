"""
Compatibility re-exports for yotta parameter types.

The canonical implementations live in `yotta.core.types`, but many users expect
CLI-related types to be importable from `yotta.cli.types`.
"""

from yotta.core.types import (  # noqa: F401
    DIRECTORY,
    EMAIL,
    FLOAT,
    INT,
    JSON_TYPE,
    PATH,
    PORT,
    STRING,
    URL_TYPE,
    UUID_TYPE,
    Choice,
    Directory,
    EnumChoice,
    File,
    JSON,
    Path,
    Port,
    Range,
    URL,
    UUID,
)

__all__ = [
    # Factories/helpers
    "Choice",
    "Directory",
    "EnumChoice",
    "File",
    "JSON",
    "Path",
    "Port",
    "Range",
    "URL",
    "UUID",
    # ParamType singleton instances
    "DIRECTORY",
    "EMAIL",
    "FLOAT",
    "INT",
    "JSON_TYPE",
    "PATH",
    "PORT",
    "STRING",
    "URL_TYPE",
    "UUID_TYPE",
]
