# Changelog

All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org).

## [Unreleased][]
- **Changes**: --inverse option to show common commits [#118][] [#134][]

[#118]: https://github.com/Brickster/git-commands/issues/118
[#134]: https://github.com/Brickster/git-commands/issues/134

## [v0.7.0][] - 2019-08-26
### Features
- **State**: extension management sub-command [#89][]
- **State**: `--ignore-extensions` renamed to `--no-show`[#91][]
- **Changes**: view changes with pathspecs [#128][]
- **Changes**: verbose option to print default when unassociated [#129][]
- **Settings**: limit listing to section names

### Changes
- **State**: standardize status show/no-show options [#130][]

### Removals
- `git-settings` cleanup
- `git-tuck` [#120][]

### Fixes
- `state --no-show-status` not respected for empty repositories [#93][]
- `changes view` breaking when HEAD is detached [#94][]
- `settings list` not handling values with newline characters [#95][]
- `changes unassociate` breaking when no association exists for the branch [#102][]
- `changes unassociate --prune` breaking when no associations exist [#103][]
- `changes unassociate --prune` breaking for new repositories [#104][]
- Associating a detached HEAD [#106][]
- `changes associate` breaking when using an invalid revision [#107][]
- `changes unassociate --dry-run` printing a message during a no-op [#108][]
- `changes associate --upstream` failing with local upstreams [#112][]
- **Snapshot**: silently not creating a stash if created too quickly [#114][]
- `state` printing header colors in some colorless scenarios [#117][]
- **Settings**: listing keys without a section [#119][]
- `settings list` failing with empty config files [#121][]
- `settings list` not properly handling unknown files [#122][]
- `changes view` not decorating when printing to a non-TTY [#124][]
- **Settings**: not handling missing system git configs [#131][]

### Documentation
- **Changes**: fix dry run description typo [#132][]
- **Settings**: remove list restriction when using options [#136][]
- **Changes**: add remote option to synopsis [#139][]

[#89]: https://github.com/Brickster/git-commands/issues/89
[#91]: https://github.com/Brickster/git-commands/issues/91
[#93]: https://github.com/Brickster/git-commands/issues/93
[#94]: https://github.com/Brickster/git-commands/issues/94
[#95]: https://github.com/Brickster/git-commands/issues/95
[#102]: https://github.com/Brickster/git-commands/issues/102
[#103]: https://github.com/Brickster/git-commands/issues/103
[#104]: https://github.com/Brickster/git-commands/issues/104
[#106]: https://github.com/Brickster/git-commands/issues/106
[#107]: https://github.com/Brickster/git-commands/issues/107
[#108]: https://github.com/Brickster/git-commands/issues/108
[#112]: https://github.com/Brickster/git-commands/issues/112
[#114]: https://github.com/Brickster/git-commands/issues/114
[#117]: https://github.com/Brickster/git-commands/issues/117
[#119]: https://github.com/Brickster/git-commands/issues/119
[#120]: https://github.com/Brickster/git-commands/issues/120
[#121]: https://github.com/Brickster/git-commands/issues/121
[#122]: https://github.com/Brickster/git-commands/issues/122
[#124]: https://github.com/Brickster/git-commands/issues/124
[#128]: https://github.com/Brickster/git-commands/issues/128
[#129]: https://github.com/Brickster/git-commands/issues/129
[#130]: https://github.com/Brickster/git-commands/issues/130
[#131]: https://github.com/Brickster/git-commands/issues/131
[#132]: https://github.com/Brickster/git-commands/issues/132
[#136]: https://github.com/Brickster/git-commands/issues/136
[#139]: https://github.com/Brickster/git-commands/issues/139

## [v0.6.1][] - 2017-01-17
### Fixed
- `git-state` printing header colors in with `--no-color` [#80][]
- `git-changes` defaulting to an ambiguous ref [#92][]

[#80]: https://github.com/Brickster/git-commands/issues/80
[#92]: https://github.com/Brickster/git-commands/issues/92

## [v0.6.0][] - 2017-01-14
### Added
- `git-tuck` options `--dry-run` and `--color` [#67][]
- `git-tuck` options for adding based on index status
- `git-reindex` for re-adding already indexed files to the index
- `-u|--upstream` option to `changes associate` [#81][]
- `git-state` extension configuration for options [#84][]
- `git-state` extension configuration for showing [#85][]
- `git-state` flags for showing/not showing custom extensions [#87][]
- `git-state` extension configuration for coloring [#88][]
- `git-state` option to never page output [#76][]
- `-d|--dry-run` option to `changes unassociate` [#71][]

### Changed
- Boolean flags only parse using `git-config` supported values [#90][]

### Removed
- The branches, log, reflog, and stashes built-in extensions were removed in favor of defining them using custom extensions [#83][]

### Fixed
- `git-changes` reporting ambiguous refs as not being a valid commit [#58][]
- `git-changes` options `--help` and `--version` not working in non-git repositories [#60][]
- `git-changes` printing an incorrect error message when using `--remote` without an upstream branch [#61][]
- `git-tuck` not preserving index changes [#62][]
- `git-tuck` attempting to run in a non-git repository [#66][]
- `git-snapshot` not preserving restoring index changes [#64][]
- `git-upstream` not working for empty/new repositories [#72][]
- `git-restash` printing a misleading message when no stashes exist [#75][]
- `git-changes` leaving empty sections when unassociating [#78][]
- `git-state` status not respecting color options
- `git-changes` not working for `--count` option [#77][]
- `git-changes` not working for empty/new repositories [#74][]
- Documentation issues [#59][] [#86][]

[#58]: https://github.com/Brickster/git-commands/issues/58
[#59]: https://github.com/Brickster/git-commands/issues/59
[#60]: https://github.com/Brickster/git-commands/issues/60
[#61]: https://github.com/Brickster/git-commands/issues/61
[#62]: https://github.com/Brickster/git-commands/issues/62
[#64]: https://github.com/Brickster/git-commands/issues/64
[#66]: https://github.com/Brickster/git-commands/issues/66
[#67]: https://github.com/Brickster/git-commands/issues/67
[#71]: https://github.com/Brickster/git-commands/issues/71
[#72]: https://github.com/Brickster/git-commands/issues/72
[#74]: https://github.com/Brickster/git-commands/issues/74
[#75]: https://github.com/Brickster/git-commands/issues/75
[#76]: https://github.com/Brickster/git-commands/issues/76
[#77]: https://github.com/Brickster/git-commands/issues/77
[#78]: https://github.com/Brickster/git-commands/issues/78
[#81]: https://github.com/Brickster/git-commands/issues/81
[#83]: https://github.com/Brickster/git-commands/issues/83
[#84]: https://github.com/Brickster/git-commands/issues/84
[#85]: https://github.com/Brickster/git-commands/issues/85
[#86]: https://github.com/Brickster/git-commands/issues/86
[#87]: https://github.com/Brickster/git-commands/issues/87
[#88]: https://github.com/Brickster/git-commands/issues/88
[#90]: https://github.com/Brickster/git-commands/issues/90

## [v0.5.0][] - 2016-04-14
### Added
- `-b|--branch` option to `upstream`
- `git-tuck` for stashing specific files
- `git-state.status.show-clean-message` configuration toggling a message in the status section when the working directory is clean
- `-q|--quiet` option to `abandon`, `restash`, and `snapshot` [#30][]
- Snapshots can now be created with a subset of files [#35][]
- Cleanup subcommand to `settings`
- Associations to `git-changes`
- Option passing to custom extensions

### Changed
- The default commit-ish for changes was renamed from `git-changes.default-branch` to `git-changes.default-commit-ish`

### Fixed
- State not working with new repositories
- Printing ANCI codes in status when using `--no-color` [#27][]
- Colored output not working on Windows machines [#28][]
- Restash not removing untracked files [#25][]
- Documentation typos

### Removed
- git-fixup

[#25]: https://github.com/Brickster/git-commands/issues/25
[#27]: https://github.com/Brickster/git-commands/issues/27
[#28]: https://github.com/Brickster/git-commands/issues/28
[#30]: https://github.com/Brickster/git-commands/issues/30
[#35]: https://github.com/Brickster/git-commands/issues/35

## [v0.4.0][] - 2015-08-26
### Added
- Section order configuration and option
- Extension name configuration

### Fixed
- Documentation typos and links

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

## [v0.1.0][] - 2015-03-02
### Added
- Everything

[Unreleased]: https://github.com/Brickster/git-commands/compare/latest...HEAD
[v0.7.0]: https://github.com/Brickster/git-commands/compare/v0.6.1...v0.7.0
[v0.6.1]: https://github.com/Brickster/git-commands/compare/v0.6.0...v0.6.1
[v0.6.0]: https://github.com/Brickster/git-commands/compare/v0.5.0...v0.6.0
[v0.5.0]: https://github.com/Brickster/git-commands/compare/v0.4.0...v0.5.0
[v0.4.0]: https://github.com/Brickster/git-commands/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/Brickster/git-commands/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/Brickster/git-commands/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/Brickster/git-commands/compare/4a8227e7ea81bcc641a142078c59cbc71f6aa4dc...v0.1.0
