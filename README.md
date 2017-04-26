# git-commands

[![Build Status](https://travis-ci.org/Brickstertwo/git-commands.svg?branch=master)](https://travis-ci.org/Brickstertwo/git-commands) [![Requirements Status](https://requires.io/github/Brickstertwo/git-commands/requirements.svg?branch=master)](https://requires.io/github/Brickstertwo/git-commands/requirements/?branch=master) [![Code Climate](https://codeclimate.com/github/Brickstertwo/git-commands/badges/gpa.svg)](https://codeclimate.com/github/Brickstertwo/git-commands) [![Test Coverage](https://codeclimate.com/github/Brickstertwo/git-commands/badges/coverage.svg)](https://codeclimate.com/github/Brickstertwo/git-commands/coverage)

A collection of custom git commands

## Install

```bash
pip install -r requirements.txt
make [install]
```
or
```bash
pip install -r requirements.txt
export PATH="$PATH:/path/to/git-commands/repository/bin"
```

## Uninstall

```bash
make uninstall
```
or
```bash
# remove the previously added line
```

## Commands
### [state][]

Used to see a more concise and comprehensive view of the working directory through custom extensions.

```bash
git state [(-s|--status)] [(-S|--no-status)]
          [--show-*] [--no-show-*]  # for each custom extension
          [(-e|--show-empty)] [(-E|--no-show-empty)]
          [(-c|--color) [WHEN]] [(-C|--no-color)]
          [(-p|--pretty)] [(-f|--format) FORMAT]
          [--clear] [--no-clear] [--no-page]
          [--ignore-extensions [EXTENSION ...]]
          [(-o|--order) SECTION [SECTION ...]]
          [(-O|--options) OPTION [OPTION ...]]
git state (-h|--help)
git state (-v|--version)
```

### [snapshot][]

Used to record the current state of the working directory without reverting it.

```bash
git snapshot [MESSAGE] [(-q|--quiet)] [-- FILE [FILE ...]]
git snapshot (-h|--help)
git snapshot (-v|--version)
```

### [changes][]

Used to list the commits between this branch and another.

```bash
git changes [view] [(-c|--count)] [(-s|--stat)] [(-d|--diff)]
                   [--color [WHEN]] [--no-color] [COMMIT-ISH]
git changes associate [(-q|--quiet)] [(-u|--upstream)] [COMMIT-ISH]
git changes unassociate [(-a|--all)] [(-p|--prune)] [(-q|--quiet)]
                        [(-d|--dry-run)]
git changes (-h|--help)
git changes (-v|--version)
```

### [settings][]

Used as a compliment to `git-config` by adding missing features.

```bash
git settings get [FILE-OPTION] [(-d|--default) VALUE] KEY
git settings destroy [(-d|--dry-run)] SECTION
git settings list [FILE-OPTION] [(-p|--pretty)]
                  [(-f|--format) FORMAT] [(-c|--count)]
                  [(-k|--keys)] [SECTION]
git settings (-h|--help)
git settings (-v|--version)
```

### [upstream][]

Used to get the current upstream branch.

```bash
git upstream [(-r|--include-remote)] [(-R|--no-include-remote)]
             [(-b|--branch)]
git upstream (-h|--help)
git upstream (-v|--version)
```

### [abandon][]

Used to drop a count or range of stashes.

```bash
git abandon [(-d|--dry-run)] [(-q|--quiet)] [START] END
git abandon (-h|--help)
git abandon (-v|--version)
```

### [restash][]

Used to restash changes.

```bash
git restash [(-q|--quiet)] [STASH]
git restash (-h|--help)
git restash (-v|--version)
```

### [tuck][]

Used to stash specific files rather than the all-or-nothing style of `git stash`.

```bash
git tuck [MESSAGE] [(-i|--ignore-deleted)|(-I|--no-ignore-deleted)]
         [(-c|--color) [WHEN]|(-C|--no-color)]
         [(-x|--indexed)|(-X|--unindexed)]
         [(-d|--dry-run)|(-q|--quiet)] -- FILE [FILE ...]
git tuck (-h|--help)
git tuck (-v|--version)
```

### [reindex][]

Used to re-add already indexed files to the index.

```bash
git reindex (-h|--help)
git reindex (-v|--version)
```

## Dependencies

- [colorama](https://pypi.python.org/pypi/colorama)
- [enum34](https://pypi.python.org/pypi/enum34)

[state]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-state.1.html
[snapshot]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-snapshot.1.html
[changes]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-changes.1.html
[settings]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-settings.1.html
[upstream]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-upstream.1.html
[abandon]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-abandon.1.html
[restash]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-restash.1.html
[tuck]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-tuck.1.html
[reindex]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-reindex.1.html
