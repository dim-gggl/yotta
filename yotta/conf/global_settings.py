"""
Global default settings for yotta.

These values act as safe fallbacks when a project settings module omits optional
attributes. They are not intended to replace a project settings module.
"""

# Apps installed in the current project (module paths).
INSTALLED_APPS: list[str] = []

# Default UI theme name.
THEME: str = "default"

# Command discovery naming mode:
# - "none": expose commands as-is (default, backward compatible)
# - "prefix": expose as "<app_label><sep><command>" (e.g. "inventory:sync")
# - "group": expose app_label as a group (e.g. "inventory sync")
COMMAND_NAMESPACE: str = "none"

# Separator used when COMMAND_NAMESPACE="prefix"
COMMAND_NAMESPACE_SEPARATOR: str = ":"

# Entry point plugin discovery for third-party apps.
# When enabled, yotta will read Python entry points to extend INSTALLED_APPS.
# Entry points should point to an importable app package/module (e.g. "my_pkg.my_app").
ENABLE_ENTRYPOINT_APPS: bool = True
ENTRYPOINT_APPS_GROUP: str = "yotta.apps"


