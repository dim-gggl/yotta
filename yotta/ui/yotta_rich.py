"""
YottaRich - Unified access to Rich and rich-click components.

This module provides a factory class that allows users to dynamically
instantiate any Rich or rich-click component without importing them directly.

Example:
    from yotta.ui import YottaRich

    # Instead of: from rich.align import Align
    align = YottaRich.generate("align", args, kwargs)

    # Instead of: from rich.table import Table
    table = YottaRich.generate("table")
"""

import importlib
from typing import Any, Dict, List, Optional, Tuple


class YottaRich:
    """
    Factory class for generating Rich and rich-click components dynamically.

    This class provides a unified interface to access all Rich and rich-click
    functionality without requiring explicit imports of each component.
    """

    # Mapping of component names to their module paths
    _RICH_COMPONENTS = {
        # Core components
        "align": "rich.align.Align",
        "bar": "rich.bar.Bar",
        "box": "rich.box",
        "columns": "rich.columns.Columns",
        "console": "rich.console.Console",
        "constrain": "rich.constrain.Constrain",
        "containers": "rich.containers",
        "control": "rich.control.Control",

        # Layout components
        "layout": "rich.layout.Layout",
        "live": "rich.live.Live",
        "panel": "rich.panel.Panel",
        "padding": "rich.padding.Padding",

        # Text and styling
        "markdown": "rich.markdown.Markdown",
        "markup": "rich.markup",
        "pretty": "rich.pretty.Pretty",
        "syntax": "rich.syntax.Syntax",
        "text": "rich.text.Text",
        "theme": "rich.theme.Theme",
        "style": "rich.style.Style",

        # Tables and trees
        "table": "rich.table.Table",
        "tree": "rich.tree.Tree",

        # Progress and status
        "progress": "rich.progress.Progress",
        "spinner": "rich.spinner.Spinner",
        "status": "rich.status.Status",

        # Prompts and interactivity
        "prompt": "rich.prompt.Prompt",
        "confirm": "rich.prompt.Confirm",
        "intprompt": "rich.prompt.IntPrompt",
        "floatprompt": "rich.prompt.FloatPrompt",

        # Rendering
        "rule": "rich.rule.Rule",
        "traceback": "rich.traceback.Traceback",
        "json": "rich.json.JSON",
        "logging": "rich.logging.RichHandler",

        # Charts and visualizations
        "segment": "rich.segment.Segment",
        "color": "rich.color.Color",
        "filesize": "rich.filesize",

        # Measuring and inspection
        "measure": "rich.measure.Measurement",
        "scope": "rich.scope",
    }

    _RICH_CLICK_COMPONENTS = {
        "richcommand": "rich_click.RichCommand",
        "richgroup": "rich_click.RichGroup",
        "richcontext": "rich_click.RichContext",
        "richhelpformatter": "rich_click.RichHelpFormatter",
    }

    @classmethod
    def generate(
        cls,
        component_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Dynamically generate and instantiate a Rich or rich-click component.

        Args:
            component_name: Name of the component to generate (case-insensitive).
                           Examples: "align", "table", "panel", "markdown", etc.
            *args: Positional arguments to pass to the component constructor.
            **kwargs: Keyword arguments to pass to the component constructor.

        Returns:
            An instance of the requested Rich or rich-click component.

        Raises:
            ValueError: If the component name is not recognized.
            ImportError: If the component cannot be imported.
            TypeError: If the component cannot be instantiated with the given arguments.

        Examples:
            >>> # Create an Align component
            >>> align = YottaRich.generate("align", "Hello", align="center")

            >>> # Create a Table
            >>> table = YottaRich.generate("table", title="My Table")

            >>> # Create a Panel
            >>> panel = YottaRich.generate("panel", "Content", title="Title")

            >>> # Create a Markdown renderer
            >>> md = YottaRich.generate("markdown", "# Hello World")
        """
        # Normalize component name to lowercase
        component_name_lower = component_name.lower()

        # Check if component exists in Rich or rich-click
        component_path = None

        if component_name_lower in cls._RICH_COMPONENTS:
            component_path = cls._RICH_COMPONENTS[component_name_lower]
        elif component_name_lower in cls._RICH_CLICK_COMPONENTS:
            component_path = cls._RICH_CLICK_COMPONENTS[component_name_lower]
        else:
            # Try to construct a path automatically for unlisted components
            # This allows for future-proofing and accessing less common components
            component_path = cls._try_auto_resolve(component_name)

        if not component_path:
            available = sorted(
                list(cls._RICH_COMPONENTS.keys()) +
                list(cls._RICH_CLICK_COMPONENTS.keys())
            )
            raise ValueError(
                f"Component '{component_name}' not found. "
                f"Available components: {', '.join(available)}"
            )

        # Import and instantiate the component
        try:
            component_class = cls._import_component(component_path)
            return component_class(*args, **kwargs)
        except ImportError as e:
            raise e(
                f"Failed to import component '{component_name}' from '{component_path}': {e}"
            )
        except TypeError as e:
            raise e(
                f"Failed to instantiate component '{component_name}' with given arguments: {e}"
            )

    @classmethod
    def _import_component(cls, component_path: str) -> type:
        """
        Import a component class from its module path.

        Args:
            component_path: Full path to the component (e.g., "rich.align.Align")

        Returns:
            The imported component class.
        """
        module_path, class_name = component_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    @classmethod
    def _try_auto_resolve(cls, component_name: str) -> Optional[str]:
        """
        Try to automatically resolve a component path for unlisted components.

        This method attempts to find components that aren't in the predefined
        mappings by trying common patterns.

        Args:
            component_name: Name of the component to resolve.

        Returns:
            Component path if found, None otherwise.
        """
        # Try common patterns
        patterns = [
            f"rich.{component_name}.{component_name.capitalize()}",
            f"rich.{component_name}.{component_name.upper()}",
            f"rich.{component_name}",
            f"rich_click.{component_name}",
        ]

        for pattern in patterns:
            try:
                if "." not in pattern.split(".")[-1]:
                    # It's a module, not a class
                    continue
                cls._import_component(pattern)
                return pattern
            except (ImportError, AttributeError) as e:
                print(e)
                input()
                continue

        return None

    @classmethod
    def list_components(cls) -> Dict[str, List[str]]:
        """
        List all available components organized by library.

        Returns:
            Dictionary with 'rich' and 'rich_click' keys containing lists of
            available component names.

        Example:
            >>> components = YottaRich.list_components()
            >>> print(components['rich'])
            ['align', 'bar', 'columns', ...]
        """
        return {
            "rich": sorted(cls._RICH_COMPONENTS.keys()),
            "rich_click": sorted(cls._RICH_CLICK_COMPONENTS.keys())
        }

    @classmethod
    def get_component_class(cls, component_name: str) -> type:
        """
        Get the component class without instantiating it.

        Useful when you need access to the class itself (e.g., for subclassing
        or accessing class methods/attributes).

        Args:
            component_name: Name of the component to get.

        Returns:
            The component class (not an instance).

        Raises:
            ValueError: If the component name is not recognized.
            ImportError: If the component cannot be imported.

        Example:
            >>> Table = YottaRich.get_component_class("table")
            >>> table = Table(title="My Table")
        """
        component_name_lower = component_name.lower()

        component_path = None
        if component_name_lower in cls._RICH_COMPONENTS:
            component_path = cls._RICH_COMPONENTS[component_name_lower]
        elif component_name_lower in cls._RICH_CLICK_COMPONENTS:
            component_path = cls._RICH_CLICK_COMPONENTS[component_name_lower]
        else:
            component_path = cls._try_auto_resolve(component_name)

        if not component_path:
            available = sorted(
                list(cls._RICH_COMPONENTS.keys()) +
                list(cls._RICH_CLICK_COMPONENTS.keys())
            )
            raise ValueError(
                f"Component '{component_name}' not found. "
                f"Available components: {', '.join(available)}"
            )

        return cls._import_component(component_path)
