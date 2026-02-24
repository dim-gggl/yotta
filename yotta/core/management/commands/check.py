import importlib
import os
from dataclasses import dataclass

import rich_click as click
from rich.console import Console
from rich.table import Table


@dataclass(frozen=True)
class _AppReport:
    app_path: str
    app_import_ok: bool
    commands_module_ok: bool
    commands_module_missing: bool
    commands_count: int
    error: str | None


def _get_root_flags(ctx: click.Context) -> dict[str, bool]:
    parent = ctx.parent
    params = getattr(parent, "params", {}) or {} if parent is not None else {}
    return {
        "quiet": bool(params.get("quiet", False)),
        "verbose": bool(params.get("verbose", False)),
        "strict": bool(params.get("strict", False)),
    }


@click.command(name="check", help="Diagnose settings, apps, and command discovery.")
@click.pass_context
def check_command(ctx: click.Context) -> None:
    console = Console()
    flags = _get_root_flags(ctx)
    quiet = flags["quiet"]
    strict = flags["strict"]

    # Settings diagnostics
    settings_error: str | None = None
    settings_module = None
    project_root = None
    env_files: list[str] = []
    installed_apps: list[str] = []
    namespace_mode = "none"
    namespace_sep = ":"

    try:
        from yotta.conf import settings

        settings_module = os.environ.get("YOTTA_SETTINGS_MODULE")
        project_root = getattr(
            settings, "_get_project_root", lambda: None
        )()  # internal but stable enough for diagnostics
        env_files = list(getattr(settings, "env_files_loaded", []))
        installed_apps_raw = getattr(settings, "INSTALLED_APPS", [])
        if installed_apps_raw is None:
            installed_apps = []
        elif isinstance(installed_apps_raw, (list, tuple)):
            installed_apps = list(installed_apps_raw)
        else:
            raise TypeError("INSTALLED_APPS must be a list or tuple of module paths.")

        namespace_mode = str(getattr(settings, "COMMAND_NAMESPACE", "none") or "none").strip().lower()
        namespace_sep = str(getattr(settings, "COMMAND_NAMESPACE_SEPARATOR", ":") or ":")
    except Exception as exc:
        settings_error = str(exc)

    console.print("[bold]yotta check[/]")

    settings_table = Table(title="Settings", show_header=False, box=None)
    settings_table.add_column("key", style="bold")
    settings_table.add_column("value")
    settings_table.add_row("YOTTA_SETTINGS_MODULE", str(settings_module or "<unset>"))
    settings_table.add_row("Project root", str(project_root or "<unknown>"))
    settings_table.add_row("Namespace mode", f"{namespace_mode!s} (sep={namespace_sep!r})")
    settings_table.add_row("Env files", ", ".join(env_files) if env_files else "<none>")
    settings_table.add_row("Installed apps", str(len(installed_apps)))
    if settings_error:
        settings_table.add_row("Status", f"[red]ERROR[/] {settings_error}")
    else:
        settings_table.add_row("Status", "[green]OK[/]")
    console.print(settings_table)

    if settings_error:
        raise click.ClickException("Settings failed to load; cannot continue.")

    # App/module diagnostics
    reports: list[_AppReport] = []
    for app_path in installed_apps:
        error: str | None = None
        app_import_ok = True
        commands_module_ok = True
        commands_module_missing = False
        commands_count = 0

        try:
            importlib.import_module(app_path)
        except Exception as exc:
            app_import_ok = False
            commands_module_ok = False
            error = f"Unable to import app '{app_path}': {exc}"
            reports.append(
                _AppReport(
                    app_path=app_path,
                    app_import_ok=app_import_ok,
                    commands_module_ok=commands_module_ok,
                    commands_module_missing=commands_module_missing,
                    commands_count=commands_count,
                    error=error,
                )
            )
            continue

        commands_module_name = f"{app_path}.commands"
        try:
            mod = importlib.import_module(commands_module_name)
            # Count click commands/groups exposed by the module
            for _attr_name, attr_value in vars(mod).items():
                if isinstance(attr_value, click.Command):
                    commands_count += 1
        except ImportError as exc:
            commands_module_ok = False
            if f"No module named '{commands_module_name}'" in str(exc):
                commands_module_missing = True
            else:
                error = f"Error importing {commands_module_name}: {exc}"
        except Exception as exc:
            commands_module_ok = False
            error = f"Error importing {commands_module_name}: {exc}"

        reports.append(
            _AppReport(
                app_path=app_path,
                app_import_ok=app_import_ok,
                commands_module_ok=commands_module_ok,
                commands_module_missing=commands_module_missing,
                commands_count=commands_count,
                error=error,
            )
        )

    if not quiet:
        apps_table = Table(title="Apps", header_style="bold", box=None)
        apps_table.add_column("app")
        apps_table.add_column("commands.py", justify="center")
        apps_table.add_column("commands", justify="right")
        apps_table.add_column("status")

        for r in reports:
            if r.error:
                status = f"[red]ERROR[/] {r.error}"
            elif r.commands_module_missing:
                status = "[yellow]WARN[/] no commands.py"
            else:
                status = "[green]OK[/]"

            apps_table.add_row(
                r.app_path,
                "[green]yes[/]"
                if r.commands_module_ok
                else ("[yellow]missing[/]" if r.commands_module_missing else "[red]error[/]"),
                str(r.commands_count),
                status,
            )
        console.print(apps_table)

    # Duplicate detection (effective exposed names)
    duplicates: dict[str, list[str]] = {}
    effective_names: dict[str, str] = {}  # effective -> source

    for app_path in installed_apps:
        commands_module_name = f"{app_path}.commands"
        try:
            mod = importlib.import_module(commands_module_name)
        except Exception:
            continue

        app_label = app_path.rsplit(".", 1)[-1]
        module_commands: list[tuple[str, click.Command]] = []
        for attr_name, attr_value in vars(mod).items():
            if isinstance(attr_value, click.Command):
                module_commands.append((attr_value.name or attr_name, attr_value))

        if namespace_mode == "group":
            effective = app_label
            src = f"{commands_module_name}:<group>"
            if effective in effective_names:
                duplicates.setdefault(effective, []).extend([effective_names[effective], src])
            else:
                effective_names[effective] = src
            continue

        for cmd_name, _cmd in module_commands:
            effective = f"{app_label}{namespace_sep}{cmd_name}" if namespace_mode == "prefix" else cmd_name
            src = f"{commands_module_name}:{cmd_name}"
            if effective in effective_names:
                duplicates.setdefault(effective, []).extend([effective_names[effective], src])
            else:
                effective_names[effective] = src

    if duplicates and not quiet:
        dup_table = Table(title="Duplicates", header_style="bold", box=None)
        dup_table.add_column("name", style="bold")
        dup_table.add_column("sources")
        for name, sources in duplicates.items():
            # de-duplicate source entries
            uniq = []
            for s in sources:
                if s not in uniq:
                    uniq.append(s)
            dup_table.add_row(name, "\n".join(uniq))
        console.print(dup_table)

    has_missing_commands = any(r.commands_module_missing for r in reports)
    has_errors = any((not r.app_import_ok) or (r.error and not r.commands_module_missing) for r in reports)
    has_duplicates = bool(duplicates)

    exit_code = 0
    if has_errors:
        exit_code = 1
    if strict and (has_missing_commands or has_duplicates):
        exit_code = 1

    if exit_code == 0:
        console.print("[green]OK[/] No blocking issues found.")
    else:
        console.print("[red]FAIL[/] Issues detected.")
    ctx.exit(exit_code)
