# git-commands

[![build](https://github.com/Brickster/git-commands/actions/workflows/build.yml/badge.svg)](https://github.com/Brickster/git-commands/actions/workflows/build.yml) [![Maintainability](https://qlty.sh/gh/Brickster/projects/git-commands/maintainability.svg)](https://qlty.sh/gh/Brickster/projects/git-commands) [![Code Coverage](https://qlty.sh/gh/Brickster/projects/git-commands/coverage.svg)](https://qlty.sh/gh/Brickster/projects/git-commands)

A collection of custom git commands

## Install

```bash
pip install --user -r requirements.txt
make [install]
```

or

```bash
pip install --user -r requirements.txt
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
git state [view] [--show-all] [(-s|--show) EXTENSION [EXTENSION ...]]
                 [(-S|--no-show) EXTENSION [EXTENSION ...]]
                 [(-e|--show-empty)] [(-E|--no-show-empty)]
                 [(-c|--color) [WHEN]] [(-C|--no-color)]
                 [(-p|--pretty)] [(-f|--format) FORMAT]
                 [--clear] [--no-clear] [--no-page]
                 [(-o|--order) SECTION [SECTION ...]]
                 [(-O|--options) OPTION [OPTION ...]]
git state extensions [list]
git state extensions create (-c|--command) COMMAND [(-n|--name) NAME]
                            [(-o|--options) OPTIONS] [--no-show]
                            [--no-color] EXTENSION
git state extensions edit [(-c|--command) COMMAND] [(-n|--name) NAME]
                          [(-o|--options) OPTIONS] [--no-show]
                          [--no-color] EXTENSION
git state extensions delete [-q] EXTENSION
git state extensions config [-f FORMAT | -p] EXTENSION
git state extensions run EXTENSION
git state (-h|--help)
git state (-v|--version)
```

### [snapshot][]

Used to record the current state of the working directory without reverting it.

```bash
git snapshot [MESSAGE] [(-r|--replace)] [(-q|--quiet)] [-- FILE [FILE ...]]
git snapshot (-h|--help)
git snapshot (-v|--version)
```

### [changes][]

Used to list the commits between this branch and another.

```bash
git changes [view] [(-l|--log)] [(-i|--inverse)] [(-c|--count)]
                   [(-s|--stat)] [(-d|--diff)] [(-u|--upstream)]
                   [--color [WHEN]] [--no-color] [COMMIT-ISH]
                   [-- FILE [FILE ...]]
git changes associate [(-q|--quiet)] [(-u|--upstream)] [COMMIT-ISH]
git changes unassociate [(-a|--all)] [(-p|--prune)] [(-q|--quiet)]
                        [(-d|--dry-run)]
git changes (-h|--help)
git changes (-v|--version)
```

### [settings][]

Used as a compliment to `git-config` by adding missing features.

```bash
git settings destroy [(-d|--dry-run)] SECTION
git settings list [FILE-OPTION] [(-p|--pretty)]
                  [(-f|--format) FORMAT] [(-c|--count)]
                  [(-s|--sections)] [(-k|--keys)] [SECTION]
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

### [reindex][]

Used to re-add already indexed files to the index.

```bash
git reindex (-h|--help)
git reindex (-v|--version)
```

## Testing and OS Support

`git-commands` has been tested using git 2.52.0 and Python 3.10 on macOS 26 Tahoe and Ubuntu Resolute Raccoon. To confirm on your own system, install [nox](https://nox.thea.codes) and run the test suite.

```bash
brew install pipx
pipx ensurepath
pipx install nox
nox
```

## Dependencies

- [colorama](https://pypi.python.org/pypi/colorama)
- [enum34](https://pypi.python.org/pypi/enum34)

[state]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickster/git-commands/main/man/man1/git-state.1.html
[snapshot]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickster/git-commands/main/man/man1/git-snapshot.1.html
[changes]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickster/git-commands/main/man/man1/git-changes.1.html
[settings]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickster/git-commands/main/man/man1/git-settings.1.html
[upstream]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickster/git-commands/main/man/man1/git-upstream.1.html
[abandon]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickster/git-commands/main/man/man1/git-abandon.1.html
[restash]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickster/git-commands/main/man/man1/git-restash.1.html
[reindex]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickster/git-commands/main/man/man1/git-reindex.1.html
