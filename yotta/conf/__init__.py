import importlib
import os
import sys
import traceback
from pathlib import Path

from yotta.conf import global_settings as _defaults


class Settings:
    def __init__(self):
        self._wrapped = None
        self._env_loaded = False
        self._sys_path_added = False
        self.debug_enabled = False
        # Load environment files early so flags like YOTTA_DEBUG are available
        # even if the caller never triggers settings module import via __getattr__.
        self._load_env()

    def _find_project_root(self) -> Path | None:
        current = Path.cwd().resolve()

        for directory in (current, *current.parents):
            manage_py = directory / "manage.py"
            if manage_py.is_file():
                try:
                    if "yotta" in manage_py.read_text(encoding="utf-8"):
                        return directory
                except OSError:
                    continue

            pyproject = directory / "pyproject.toml"
            settings_py = directory / "settings.py"
            if pyproject.is_file() and settings_py.is_file():
                try:
                    content = pyproject.read_text(encoding="utf-8")
                    if any(name in content for name in ('"yotta"', "'yotta'", '"yotta-framework"', "'yotta-framework'")):
                        return directory
                except OSError:
                    continue

        return None

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

        project_root = self._find_project_root()
        base_path = str(project_root or Path.cwd())

        # Add the project root to the path to find the settings file (once)
        if not self._sys_path_added:
            sys.path.insert(0, base_path)
            self._sys_path_added = True

        try:
            self._wrapped = importlib.import_module(settings_module)
        except ImportError as e:
            if self.debug_enabled:
                traceback.print_exc()
            raise ImportError(f"Unable to import settings '{settings_module}': {e}") from e

    def _load_env(self) -> dict[str, str]:
        """Lightweight .env loader to populate os.environ before settings import."""
        if self._env_loaded:
            return {}
        loaded = {}
        project_root = self._find_project_root()
        env_root = project_root or Path.cwd()
        for env_file in (".env", ".env.local"):
            env_path = env_root / env_file
            if not env_path.exists():
                continue
            with env_path.open(encoding="utf-8") as f:
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
        """Proxy to access the attributes of the loaded settings module.

        Falls back to ``yotta.conf.global_settings`` when the project module
        does not define the requested attribute, so optional settings always
        have a sensible default.
        """
        if self._wrapped is None:
            self._setup()
        try:
            return getattr(self._wrapped, name)
        except AttributeError:
            return getattr(_defaults, name)


# Singleton exported
settings = Settings()
