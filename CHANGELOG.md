# Changelog

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org).

## [Unreleased][]
### Added
- changes: option to show changes as a stat
- changes: option to show changes as a diff
- changes: option to show changes compared to a known remote branch
- fixup: option to add all files
- fixup: option to add only already known files
- settings: option to list only the keys for a section
- state: option to clear the screen (or not) before printing
- state: ability to specify when to print colors rather than only always or never
- state: ability to create custom sections
- Missing documentation in `--help` messages

### Changed
- state: the status section now prints all untracked files rather than just their directory
- state: the output no longer defaults to colored when piped
- Error messages are now printed to standard error

### Fixed
- restash: printing a success message even if the reverse patch didn't apply
- restash: error message when an invalid stash was supplied
- settings: printing a blank line when a config had no value
- settings: printing a blank line during a dry destroy
- settings: printing a blank line when list empty sections
- snapshot: being overly talkative when the snapshot only contained untracked files
- state: color codes still being printed even when told not to
- state: color.status config value getting overridden
- state: error message when run in a non-Git directory
- state: extensions not printing when empty even if `-e|--show-empty` is included #21
- upstream: printing a blank line when no upstream branch exists
- Documentation typos
- Makefile install/uninstall

## [v0.2.0][] - 2015-04-12
### Changed
- Re-written in Python
- `git-settings` no longer defaults to key retrieval when no subcommand is specified

## v0.1.0 - 2015-03-02
### Added
- Everything

[Unreleased]: https://github.com/Brickstertwo/git-commands/compare/v0.2.0...HEAD
[v0.2.0]: https://github.com/Brickstertwo/git-commands/compare/v0.1.0...v0.2.0
