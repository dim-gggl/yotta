import os
import importlib
import sys
import traceback
from typing import Dict, Optional


class Settings:
    def __init__(self):
        self._wrapped = None
        self._env_loaded = False
        self._sys_path_added = False
        self.debug_enabled = False
        # Load environment files early so flags like YOTTA_DEBUG are available
        # even if the caller never triggers settings module import via __getattr__.
        self._load_env()

    def _setup(self):
        """Load the settings module defined in the environment."""
        self._load_env()
        settings_module = os.environ.get("YOTTA_SETTINGS_MODULE")
        if not settings_module:
            yotta_env = os.environ.get("YOTTA_ENV")
            if yotta_env:
                settings_module = f"settings_{yotta_env}"
                os.environ["YOTTA_SETTINGS_MODULE"] = settings_module

        if not settings_module:
            raise ImportError(
                "YOTTA_SETTINGS_MODULE is not defined. "
                "Set it in your environment, in a .env/.env.local file, or via manage.py before running commands."
            )

        # Add the current directory to the path to find the settings file (once)
        if not self._sys_path_added:
            sys.path.insert(0, os.getcwd())
            self._sys_path_added = True

        try:
            self._wrapped = importlib.import_module(settings_module)
        except ImportError as e:
            if self.debug_enabled:
                traceback.print_exc()
            raise ImportError(f"Unable to import settings '{settings_module}': {e}")

    def _load_env(self) -> Dict[str, str]:
        """Lightweight .env loader to populate os.environ before settings import."""
        if self._env_loaded:
            return {}
        loaded = {}
        for env_file in (".env", ".env.local"):
            env_path = os.path.join(os.getcwd(), env_file)
            if not os.path.exists(env_path):
                continue
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#") or "=" not in stripped:
                        continue
                    key, value = stripped.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    loaded[key] = value
                    if env_file == ".env.local":
                        os.environ[key] = value
                    else:
                        os.environ.setdefault(key, value)
        self.debug_enabled = self._get_bool_env("YOTTA_DEBUG", default=False)
        self._env_loaded = True
        return loaded

    def _get_bool_env(self, key: str, default: bool = False) -> bool:
        val = os.environ.get(key)
        if val is None:
            return default
        return str(val).lower() in ("1", "true", "yes", "on")

    def __getattr__(self, name):
        """Proxy to access the attributes of the loaded settings module."""
        if self._wrapped is None:
            self._setup()
        return getattr(self._wrapped, name)


# Singleton exported
settings = Settings()
