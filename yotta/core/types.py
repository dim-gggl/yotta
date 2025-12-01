import re
import os
import rich_click as click

class yottaType(click.ParamType):
    """Base class for our custom types."""
    pass

# --- EMAIL VALIDATOR ---
class EmailType(yottaType):
    name = "email"

    def convert(self, value, param, ctx):
        # Simple regex to validate the format
        if re.match(r"[^@]+@[^@]+\.[^@]+", value):
            return value
        self.fail(f"'{value}' n'est pas une adresse email valide.", param, ctx)

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
        # 1. Check the extension before even opening the file
        if self.extension and not value.endswith(self.extension):
            self.fail(f"Le fichier doit avoir l'extension '{self.extension}'.", param, ctx)
        
        # 2. Standard behavior (opening the file)
        return super().convert(value, param, ctx)

# --- PRACTICAL ALIASES ---
# We expose the instances directly so they can be used without parentheses when possible
EMAIL = EmailType()
INT = click.INT
FLOAT = click.FLOAT
STRING = click.STRING

def Range(min=None, max=None):
    """Helper to create a range."""
    return click.IntRange(min, max)

def File(mode='r', extension=None):
    """Factory for our improved file type."""
    return FileType(mode=mode, extension=extension)