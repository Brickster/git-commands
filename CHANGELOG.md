# Changelog

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org).

## [v0.3.0][] - 2015-08-17
### Added
- `changes`
    - Option to show changes as a stat
    - Option to show changes as a diff
    - Option to show changes compared to a known remote branch
- `fixup`
    - Option to add all files
    - Option to add only already known files
- `settings`
    - Option to list only the keys for a section
- `state`
    - Option to clear the screen (or not) before printing
    - Ability to specify when to print colors rather than only always or never
    - Ability to create custom sections
- Missing documentation in `--help` messages

### Changed
- `state`
    - The status section now prints all untracked files rather than just their directory
    - The output no longer defaults to colored when piped
- Error messages are now printed to standard error

### Fixed
- `restash`
    - Printing a success message even if the reverse patch didn't apply
    - Error message when an invalid stash was supplied
- `settings`
    - Printing a blank line when a config had no value
    - Printing a blank line during a dry destroy
    - Printing a blank line when list empty sections
- `snapshot`
    - Being overly talkative when the snapshot only contained untracked files
- `state`
    - Color codes still being printed even when told not to
    - Color.status config value getting overridden
    - Error message when run in a non-Git directory
    - Extensions not properly handling quoted strings #20
    - Extensions not printing when empty even if `-e|--show-empty` is included #21
- `upstream`
    - Printing a blank line when no upstream branch exists
- Documentation typos
- Makefile install/uninstall

## [v0.2.0][] - 2015-04-12
### Changed
- Re-written in Python
- `git-settings` no longer defaults to key retrieval when no subcommand is specified

## v0.1.0 - 2015-03-02
### Added
- Everything

[v0.3.0]: https://github.com/Brickstertwo/git-commands/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/Brickstertwo/git-commands/compare/v0.1.0...v0.2.0
