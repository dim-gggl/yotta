# Scaffolding Remarques Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Apply scaffold fixes from `REMARQUES.md` for startproject/startapp robustness and correct pyproject metadata.

**Architecture:** Adjust startproject templates (pyproject, spinner timing) and startapp flow (project root detection, app name validation) without altering unrelated commands. Preserve existing CLI options and outputs.

**Tech Stack:** Python 3.10+, uv, click/rich-click, filesystem ops.

### Task 1: Stabilize flat-layout pyproject build metadata

**Files:**
- Modify: `yotta/core/management/commands/startproject.py:get_pyproject_template`
- Test: manual generation

**Step 1: Add build-system and setuptools config for flat layout matching repo root.**
**Step 2: Keep src layout conditional but ensure flat layout also sets `[build-system]` with `setuptools`/`wheel`.**
**Step 3: Ensure uv/pip install works without implicit defaults.**

Verification: `uv run python -c "from yotta.core.management.commands.startproject import StartProjectCommand; print('pyproject' in StartProjectCommand().get_pyproject_template('demo'))"` and manual inspection of generated file.

### Task 2: Remove artificial 1s delay in startproject spinner

**Files:**
- Modify: `yotta/core/management/commands/startproject.py:run`

**Step 1: Drop `time.sleep(1)` inside Live spinner.**
**Step 2: Ensure spinner still wraps create_structure call.**

Verification: `uv run python -m compileall yotta` (syntax) and eyeball logic.

### Task 3: Robust project root detection for startapp

**Files:**
- Modify: `yotta/core/management/commands/startapp.py:run`
- (Optional new helper inside same module)

**Step 1: Implement upward search from cwd for markers (`.yotta`, `manage.py`, `pyproject.toml`) to determine project root.**
**Step 2: Resolve package root respecting existing `src/<project>` once; avoid duplicate `src/project` segments.**
**Step 3: Maintain `--dst` override as highest priority.**

Verification: unit-like manual checks via `uv run python - <<'PY' ...` simulating cwd/paths; `uv run python -m compileall yotta`.

### Task 4: Validate app_name before generation

**Files:**
- Modify: `yotta/core/management/commands/startapp.py:run`

**Step 1: Reject names with path separators or non-identifier patterns; disallow keywords.**
**Step 2: Emit clear error and abort before writing files.**

Verification: `uv run python - <<'PY' ...` calling StartAppCommand.run with invalid names; expect printed error; `python -m compileall` stays clean.
