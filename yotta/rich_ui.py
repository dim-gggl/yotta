"""
RichUI - Unified access point for all Rich library components.

This module provides a singleton class that exposes all Rich components
as class attributes, allowing easy instantiation without multiple imports.

Example:
    from yotta.rich_ui import rich

    # Instead of: from rich.console import Console
    console = rich.console()

    # Instead of: from rich.table import Table
    table = rich.table(title="My Table")

    # Instead of: from rich.panel import Panel
    panel = rich.panel("Content", title="Title")
"""

# Core Rich imports
from rich.align import Align
from rich.bar import Bar
from rich.box import Box, ROUNDED, HEAVY, DOUBLE, MINIMAL
from rich.columns import Columns
from rich.console import Console, Group
from rich.constrain import Constrain
from rich.control import Control
from rich.errors import *

# Layout components
from rich.layout import Layout
from rich.live import Live
from rich.padding import Padding
from rich.panel import Panel

# Text and styling
from rich.color import Color
from rich.emoji import Emoji
from rich.highlighter import *
from rich.json import JSON
from rich.jupyter import JupyterMixin
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.markup import escape, render
from rich.pretty import Pretty, pprint, pretty_repr
from rich.style import Style
from rich.styled import Styled
from rich.syntax import Syntax
from rich.text import Text
from rich.theme import Theme

# Tables and trees
from rich.table import Table
from rich.tree import Tree

# Progress and status
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
    MofNCompleteColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeElapsedColumn
)
from rich.spinner import Spinner
from rich.status import Status

# Prompts and interactivity
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt, InvalidResponse

# Rendering and display
from rich.rule import Rule
from rich.segment import Segment
from rich.traceback import Traceback, install as install_traceback

# Measuring and utilities
from rich.measure import Measurement
from rich.protocol import is_renderable
from rich.scope import render_scope
from rich.screen import Screen

# File operations
from rich.filesize import decimal

# Containers
try:
    from rich.containers import Renderables
except ImportError:
    Renderables = None


class RichUI:
    """
    Singleton class providing unified access to all Rich components.

    This class exposes Rich components as callable attributes, allowing
    users to instantiate components without explicit imports.

    Usage:
        from yotta.rich_ui import rich

        # Create components directly
        console = rich.console()
        table = rich.table(title="Data")
        panel = rich.panel("Hello World")
    """

    def __init__(self):
        """Initialize RichUI with all Rich component references."""
        # Core components
        self._console = Console
        self._group = Group

        # Layout
        self._align = Align
        self._columns = Columns
        self._constrain = Constrain
        self._layout = Layout
        self._padding = Padding

        # Containers and panels
        self._panel = Panel

        # Text and styling
        self._color = Color
        self._emoji = Emoji
        self._markup = render
        self._escape = escape
        self._pretty = Pretty
        self._style = Style
        self._styled = Styled
        self._syntax = Syntax
        self._text = Text
        self._theme = Theme

        # Tables and trees
        self._table = Table
        self._tree = Tree

        # Progress and status
        self._progress = Progress
        self._spinner = Spinner
        self._status = Status
        self._live = Live

        # Progress columns
        self._bar_column = BarColumn
        self._text_column = TextColumn
        self._time_remaining_column = TimeRemainingColumn
        self._spinner_column = SpinnerColumn
        self._mofn_complete_column = MofNCompleteColumn
        self._download_column = DownloadColumn
        self._transfer_speed_column = TransferSpeedColumn
        self._time_elapsed_column = TimeElapsedColumn

        # Prompts
        self._prompt = Prompt
        self._confirm = Confirm
        self._int_prompt = IntPrompt
        self._float_prompt = FloatPrompt

        # Rendering
        self._rule = Rule
        self._segment = Segment
        self._traceback = Traceback
        self._markdown = Markdown
        self._json = JSON

        # Utilities
        self._bar = Bar
        self._box = Box
        self._control = Control
        self._measurement = Measurement
        self._screen = Screen

        # Box styles
        self.ROUNDED = ROUNDED
        self.HEAVY = HEAVY
        self.DOUBLE = DOUBLE
        self.MINIMAL = MINIMAL

        # Renderables container
        if Renderables:
            self._renderables = Renderables

    # Core components
    def console(self, *args, **kwargs) -> Console:
        """Create a Rich Console instance."""
        return self._console(*args, **kwargs)

    def group(self, *args, **kwargs) -> Group:
        """Create a Group of renderables."""
        return self._group(*args, **kwargs)

    # Layout components
    def align(self, *args, **kwargs) -> Align:
        """Create an Align component for alignment."""
        return self._align(*args, **kwargs)

    def columns(self, *args, **kwargs) -> Columns:
        """Create a Columns layout."""
        return self._columns(*args, **kwargs)

    def constrain(self, *args, **kwargs) -> Constrain:
        """Create a Constrain component."""
        return self._constrain(*args, **kwargs)

    def layout(self, *args, **kwargs) -> Layout:
        """Create a Layout."""
        return self._layout(*args, **kwargs)

    def padding(self, *args, **kwargs) -> Padding:
        """Create a Padding component."""
        return self._padding(*args, **kwargs)

    # Containers and panels
    def panel(self, *args, **kwargs) -> Panel:
        """Create a Panel."""
        return self._panel(*args, **kwargs)
    
    def panel_fit(self, *args, **kwargs) -> Panel:
        """Create a Panel with fit."""
        return Panel.fit(*args, **kwargs)

    # Text and styling
    def color(self, *args, **kwargs) -> Color:
        """Create a Color."""
        return self._color(*args, **kwargs)

    def emoji(self, *args, **kwargs) -> Emoji:
        """Create an Emoji."""
        return self._emoji(*args, **kwargs)

    def pretty(self, *args, **kwargs) -> Pretty:
        """Create a Pretty representation."""
        return self._pretty(*args, **kwargs)

    def style(self, *args, **kwargs) -> Style:
        """Create a Style."""
        return self._style(*args, **kwargs)

    def styled(self, *args, **kwargs) -> Styled:
        """Create a Styled component."""
        return self._styled(*args, **kwargs)

    def syntax(self, *args, **kwargs) -> Syntax:
        """Create a Syntax highlighter."""
        return self._syntax(*args, **kwargs)

    def text(self, *args, **kwargs) -> Text:
        """Create a Text component."""
        return self._text(*args, **kwargs)

    def theme(self, *args, **kwargs) -> Theme:
        """Create a Theme."""
        return self._theme(*args, **kwargs)

    # Tables and trees
    def table(self, *args, **kwargs) -> Table:
        """Create a Table."""
        return self._table(*args, **kwargs)

    def tree(self, *args, **kwargs) -> Tree:
        """Create a Tree."""
        return self._tree(*args, **kwargs)

    # Progress and status
    def progress(self, *args, **kwargs) -> Progress:
        """Create a Progress bar."""
        return self._progress(*args, **kwargs)

    def spinner(self, *args, **kwargs) -> Spinner:
        """Create a Spinner."""
        return self._spinner(*args, **kwargs)

    def status(self, *args, **kwargs) -> Status:
        """Create a Status indicator."""
        return self._status(*args, **kwargs)

    def live(self, *args, **kwargs) -> Live:
        """Create a Live display."""
        return self._live(*args, **kwargs)

    # Progress columns
    def bar_column(self, *args, **kwargs) -> BarColumn:
        """Create a BarColumn for Progress."""
        return self._bar_column(*args, **kwargs)

    def text_column(self, *args, **kwargs) -> TextColumn:
        """Create a TextColumn for Progress."""
        return self._text_column(*args, **kwargs)

    def time_remaining_column(self, *args, **kwargs) -> TimeRemainingColumn:
        """Create a TimeRemainingColumn for Progress."""
        return self._time_remaining_column(*args, **kwargs)

    def spinner_column(self, *args, **kwargs) -> SpinnerColumn:
        """Create a SpinnerColumn for Progress."""
        return self._spinner_column(*args, **kwargs)

    # Prompts
    def prompt(self, *args, **kwargs):
        """Create or use Prompt."""
        if args or kwargs:
            return self._prompt.ask(*args, **kwargs)
        return self._prompt

    def confirm(self, *args, **kwargs):
        """Create or use Confirm prompt."""
        if args or kwargs:
            return self._confirm.ask(*args, **kwargs)
        return self._confirm

    def int_prompt(self, *args, **kwargs):
        """Create or use IntPrompt."""
        if args or kwargs:
            return self._int_prompt.ask(*args, **kwargs)
        return self._int_prompt

    def float_prompt(self, *args, **kwargs):
        """Create or use FloatPrompt."""
        if args or kwargs:
            return self._float_prompt.ask(*args, **kwargs)
        return self._float_prompt

    # Rendering
    def rule(self, *args, **kwargs) -> Rule:
        """Create a Rule."""
        return self._rule(*args, **kwargs)

    def segment(self, *args, **kwargs) -> Segment:
        """Create a Segment."""
        return self._segment(*args, **kwargs)

    def traceback(self, *args, **kwargs) -> Traceback:
        """Create a Traceback."""
        return self._traceback(*args, **kwargs)

    def markdown(self, *args, **kwargs) -> Markdown:
        """Create a Markdown renderer."""
        return self._markdown(*args, **kwargs)

    def json(self, *args, **kwargs) -> JSON:
        """Create a JSON renderer."""
        return self._json(*args, **kwargs)

    # Utilities
    def bar(self, *args, **kwargs) -> Bar:
        """Create a Bar."""
        return self._bar(*args, **kwargs)

    def box_style(self, name: str = "ROUNDED") -> Box:
        """Get a box style by name."""
        return getattr(self, name, ROUNDED)

    def control(self, *args, **kwargs) -> Control:
        """Create a Control."""
        return self._control(*args, **kwargs)

    def measurement(self, *args, **kwargs) -> Measurement:
        """Create a Measurement."""
        return self._measurement(*args, **kwargs)

    def screen(self, *args, **kwargs) -> Screen:
        """Create a Screen."""
        return self._screen(*args, **kwargs)

    # Helper methods
    def pprint(self, *args, **kwargs):
        """Pretty print using Rich."""
        return pprint(*args, **kwargs)

    def pretty_repr(self, *args, **kwargs):
        """Get pretty representation."""
        return pretty_repr(*args, **kwargs)

    def install_traceback(self, **kwargs):
        """Install Rich traceback handler."""
        return install_traceback(**kwargs)

    def is_renderable(self, obj) -> bool:
        """Check if an object is renderable."""
        return is_renderable(obj)

    def render_scope(self, *args, **kwargs):
        """Render scope."""
        return render_scope(*args, **kwargs)

    # Markup utilities
    def escape_markup(self, text: str) -> str:
        """Escape markup in text."""
        return escape(text)

    def render_markup(self, *args, **kwargs):
        """Render markup."""
        return render(*args, **kwargs)


# Singleton instance
rich = RichUI()

# Export commonly used items
__all__ = [
    "rich",
    "RichUI",
    # Re-export some commonly used classes for direct import
    "Console",
    "Table",
    "Panel",
    "Text",
    "Style",
    "Theme",
    "Progress",
    "Syntax",
    "Markdown",
    "Tree",
    "Rule",
]
