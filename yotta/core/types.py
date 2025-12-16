import json
import os
import re
import uuid
from enum import Enum
from typing import Sequence

import rich_click as click


class yottaType(click.ParamType):
    """Base class for yotta custom types."""
    pass


# --- EMAIL VALIDATOR ---
class EmailType(yottaType):
    name = "email"

    def convert(self, value, param, ctx):
        if re.match(r"[^@]+@[^@]+\.[^@]+", value):
            return value
        self.fail(f"'{value}' is not a valid email address.", param, ctx)


# --- ADVANCED FILE VALIDATOR ---
class FileType(click.File):
    """
    A file type that can check the extension.
    Ex: FileType('w', extension='.csv')
    """

    def __init__(self, mode='r', encoding=None, errors='strict', lazy=None, atomic=False, extension=None):
        super().__init__(mode, encoding, errors, lazy, atomic)
        self.extension = extension

    def convert(self, value, param, ctx):
        if self.extension and not value.endswith(self.extension):
            self.fail(f"File must have extension '{self.extension}'.", param, ctx)
        return super().convert(value, param, ctx)


class DirectoryType(click.Path):
    """Directory path that must exist."""

    def __init__(self):
        super().__init__(exists=True, file_okay=False, dir_okay=True, writable=False, readable=True)


class PathType(click.Path):
    """File or directory path, must exist by default."""

    def __init__(self, exists: bool = True, dir_okay: bool = True, file_okay: bool = True):
        super().__init__(exists=exists, dir_okay=dir_okay, file_okay=file_okay, readable=True)


class UUIDType(yottaType):
    name = "uuid"

    def convert(self, value, param, ctx):
        try:
            return uuid.UUID(str(value))
        except Exception:
            self.fail(f"'{value}' is not a valid UUID.", param, ctx)


class URLType(yottaType):
    name = "url"

    def convert(self, value, param, ctx):
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            return value
        self.fail(f"'{value}' is not a valid URL (must start with http:// or https://).", param, ctx)


class JSONType(yottaType):
    """
    Accepts either a JSON string or a path to a JSON file.
    Returns Python object (dict/list/etc).
    """
    name = "json"

    def convert(self, value, param, ctx):
        if isinstance(value, str) and os.path.exists(value):
            try:
                with open(value, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.fail(f"Unable to load JSON file '{value}': {e}", param, ctx)
        try:
            return json.loads(value)
        except Exception as e:
            self.fail(f"Unable to parse JSON value: {e}", param, ctx)


class PortType(yottaType):
    name = "port"

    def __init__(self, min_port: int = 1, max_port: int = 65535):
        self.min_port = min_port
        self.max_port = max_port

    def convert(self, value, param, ctx):
        try:
            port = int(value)
        except Exception:
            self.fail(f"'{value}' is not a valid port number.", param, ctx)
        if not (self.min_port <= port <= self.max_port):
            self.fail(f"Port must be between {self.min_port} and {self.max_port}.", param, ctx)
        return port


def Choice(options: Sequence[str], case_sensitive: bool = False) -> click.Choice:
    """Enum-like choice helper."""
    return click.Choice(list(options), case_sensitive=case_sensitive)


def EnumChoice(enum_cls: type[Enum], case_sensitive: bool = False) -> click.Choice:
    """Choice helper derived from a Python Enum."""
    values = [e.value for e in enum_cls]
    return click.Choice(values, case_sensitive=case_sensitive)


# --- PRACTICAL ALIASES ---
EMAIL = EmailType()
INT = click.INT
FLOAT = click.FLOAT
STRING = click.STRING
DIRECTORY = DirectoryType()
PATH = PathType()
UUID_TYPE = UUIDType()
URL = URLType()
JSON = JSONType()
PORT = PortType()


def Range(min=None, max=None):
    """Helper to create a range."""
    return click.IntRange(min, max)


def File(mode='r', extension=None):
    """Factory for our improved file type."""
    return FileType(mode=mode, extension=extension)


def Directory():
    """Factory for directory type requiring existence."""
    return DirectoryType()


def Path(exists: bool = True, dir_okay: bool = True, file_okay: bool = True):
    """Factory for path type with sensible defaults."""
    return PathType(exists=exists, dir_okay=dir_okay, file_okay=file_okay)


def UUID():
    """Factory for UUID type."""
    return UUIDType()


def URL():
    """Factory for URL type."""
    return URLType()


def JSON():
    """Factory for JSON (string or file) type."""
    return JSONType()


def Port(min_port: int = 1, max_port: int = 65535):
    """Factory for port type."""
    return PortType(min_port=min_port, max_port=max_port)
