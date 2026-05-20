# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

A collection of custom Git commands that extend Git's built-in functionality. Each command is a standalone Python script installed into `$PATH` and invoked as `git <command>`.

The 8 commands: `git state`, `git snapshot`, `git changes`, `git settings`, `git upstream`, `git abandon`, `git restash`, `git reindex`.

## Commands

```bash
# Setup (once)
brew install pipx && pipx ensurepath
pipx install nox
# Install qlty (required for `nox -s quality`): https://qlty.sh

# Run quality + tests
nox

# Run a single session
nox -s quality
nox -s typecheck
nox -s tests

# Pass args to pytest
nox -s tests -- -k "test_name"
nox -s tests -- tests/unit/test_state.py
nox -s tests -- --no-skip      # include tests skipped by default locally (as CI does)

# Reuse existing venv (skip reinstalling deps)
nox -r
```

Tests are discovered via `pytest.ini`. Some tests are skipped in local builds by default; `--no-skip` runs everything as CI does.

## Architecture

```
bin/
  git-state, git-snapshot, ...   # entry points — thin argparse wrappers
  commands/
    state.py, snapshot.py, ...   # core logic per command
    stateextensions/             # pluggable extensions for `git state`
      status.py                  # built-in extension
    utils/
      git.py                     # git operation wrappers
      execute.py                 # subprocess wrapper
      messages.py                # info/warn/error output helpers
      directories.py             # directory helpers
      parse_*.py                 # shared argparse helpers
tests/
  layers.py                      # test layer base classes (Unit, Functional, per-command)
  unit/                          # per-command unit tests
    testutils.py                 # unit test helpers
    stateextensions/             # tests for stateextensions/
    utils/                       # tests for commands/utils/
  functional/                    # integration tests against real git repos
    testutils.py                 # functional test helpers
    test_issue_reproductions.py  # regression tests for specific issues
```

Each `bin/git-*` entry point parses arguments and delegates to the matching `commands/*.py` module. Shared behavior (running git, printing messages, resolving paths) lives in `commands/utils/`.

### `git state` extensions

`git state` supports pluggable extensions — Python modules that contribute additional sections to its output. Extensions live in `commands/stateextensions/` and follow the pattern in `status.py`. The entry point discovers and loads them by convention.

## Key Conventions

- **Subprocess calls**: always go through `utils/execute.py`, not bare `subprocess`.
- **Output**: use `utils/messages.py` (`info`, `warn`, `error`) rather than `print`.
- **Argparse**: reuse helpers from `utils/parse_*.py` for flags that appear across multiple commands.
- **Python version**: targets Python 3.10+; `from __future__ import` guards are legacy and can be ignored.

## Workflow

After implementing a plan, suggest a commit message following [Conventional Commits](https://www.conventionalcommits.org/) format, max 72 characters.
