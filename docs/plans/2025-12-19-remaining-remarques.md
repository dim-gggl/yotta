# Remaining Remarques Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Address the remaining `REMARQUES.md` items: startcommand identifier validation, quieter loader errors, spinner theme alignment, console alias dedupe, and README quick-start adjustments.

**Architecture:** Touch only targeted modules: startcommand prompt validation, loader error handling, spinner styling via settings theme, console export cleanup, and README instructions. Preserve existing public APIs and behavior except where tightened validation or quieter logs are required.

**Tech Stack:** Python 3.10+, click/rich, textual, pytest.

### Task 1: Tighten startcommand identifier validation

**Files:**
- Modify: `yotta/core/management/commands/startcommand.py`
- Tests: `yotta/core/tests/test_startcommand.py`, `yotta/core/tests/test_startcommand_render.py`

**Step 1: Write failing tests** for rejecting invalid command/argument/option names (non-identifiers, keywords, leading digits) and re-prompting or erroring appropriately.  
**Step 2: Run tests to see failures.**  
**Step 3: Implement validation in `_prompt_identifier` and `_prompt_command_config` (keywords, identifiers).**  
**Step 4: Re-run tests to confirm green.**

### Task 2: Reduce loader traceback noise

**Files:**
- Modify: `yotta/core/loader.py`
- Tests: `yotta/core/tests/test_loader.py`

**Step 1: Add failing test ensuring non-strict/non-verbose ImportError hides traceback unless `YOTTA_DEBUG` or `--verbose` is set.**  
**Step 2: Run to observe failure.**  
**Step 3: Implement conditional traceback suppression (summary only) unless debug/verbose.**  
**Step 4: Re-run tests to confirm green.**

### Task 3: Align spinner theme with active theme

**Files:**
- Modify: `yotta/ui/spinner.py`
- Tests: `yotta/ui/tests/test_spinner.py` (extend)

**Step 1: Add failing test asserting spinner uses theme passed to `YottaConsole` (no forced DEFAULT_THEME).**  
**Step 2: Implement theme selection using console theme/settings instead of constant.**  
**Step 3: Re-run tests.**

### Task 4: Remove duplicate yottaConsole alias

**Files:**
- Modify: `yotta/ui/console.py`
- Tests: `yotta/ui/tests/test_spinner.py` or new simple import test if needed

**Step 1: Adjust file to define alias once; add/adjust test if needed to ensure import works.**  
**Step 2: Run tests.**

### Task 5: Update README Quick Start to prefer uv run

**Files:**
- Modify: `README.md`

**Step 1: Update Quick Start commands to use `uv run yotta startproject ...` / `uv run python manage.py ...`.**  
**Step 2: Proofread for English and consistency.**

### Verification

- `uv run python -m pytest` (or targeted suites after each task)  
- `uv run python -m compileall yotta`  
- Manual doc review for README changes.
