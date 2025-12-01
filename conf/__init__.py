import os
import importlib
import sys

class Settings:
    def __init__(self):
        self._wrapped = None

    def _setup(self):
        """Load the settings module defined in the environment."""
        settings_module = os.environ.get("yotta_SETTINGS_MODULE")
        if not settings_module:
            raise ImportError(
                "yotta_SETTINGS_MODULE is not defined. "
                "Please ensure you are passing through manage.py to load the settings."
            )
        
        # Add the current directory to the path to find the settings file
        sys.path.insert(0, os.getcwd())
        
        try:
            self._wrapped = importlib.import_module(settings_module)
        except ImportError as e:
            raise ImportError(f"Unable to import settings '{settings_module}': {e}")

    def __getattr__(self, name):
        """Proxy to access the attributes of the loaded settings module."""
        if self._wrapped is None:
            self._setup()
        return getattr(self._wrapped, name)

# Singleton exported
settings = Settings()