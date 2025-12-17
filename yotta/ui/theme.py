from rich.theme import Theme

# A default theme for the console inspired by modern conventions
DEFAULT_THEME = Theme({
    "primary": "orange_red1",
    "secondary": "bright_cyan",
    "success": "bold bright_green",
    "warning": "bold yellow3",
    "error": "bold red3",
    "info": "bold blue_violet",
    "header": "bold orange_red1",
})


# An alternate theme with a darker, neon-ish palette.
DARK_THEME = Theme(
    {
        "primary": "deep_sky_blue1",
        "secondary": "bright_magenta",
        "success": "bold spring_green2",
        "warning": "bold gold1",
        "error": "bold hot_pink3",
        "info": "bold dodger_blue2",
        "header": "bold deep_sky_blue1",
    }
)


THEMES = {
    "default": DEFAULT_THEME,
    "dark": DARK_THEME,
}


def resolve_theme(theme_name: str | None) -> Theme:
    """
    Resolve a theme name to a Rich Theme with a safe fallback.

    Unknown or empty names return DEFAULT_THEME.
    """
    if not theme_name:
        return DEFAULT_THEME
    return THEMES.get(str(theme_name).strip().lower(), DEFAULT_THEME)