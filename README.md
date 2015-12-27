# git-commands

A collection of custom git commands

## Install

```bash
make [install]
```
or
```bash
export PATH="$PATH:/path/to/git-commands/repository/bin"
```

See the dependencies section for other installation details.

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

Used to see a more concise and comprehensive view of the working directory. The output includes results from git status, git log, and git branch.

```bash
git state [(-l|--log) <count>] [(-L|--no-log)] [--full-log]
          [(-r|--reflog) <count>] [(-R|--no-reflog)] [--full-reflog]
          [(-s|--status)] [(-S|--no-status)]
          [(-b|--branches)] [(-B|--no-branches)]
          [(-t|--stashes)] [(-T|--no-stashes)]
          [(-e|--show-empty)] [(-E|--no-show-empty)]
          [(-c|--color) [when]] [(-C|--no-color)]
          [(-p|--pretty)] [(-f|--format) <format>]
          [--clear] [--no-clear]
          [--ignore-extensions [<extension> ...]]
          [(-o|--order) <section> [<section> ...]]
git state (-h|--help)
git state (-v|--version)
```

### [snapshot][]

Used to record the current state of the working directory without reverting it.

```bash
git snapshot [(-q|--quiet)] <message>
git snapshot (-h|--help)
git snapshot (-v|--version)
```

### [changes][]

Used to list the commits between this branch and another.

```bash
git changes [(-b|--branch) <branch>] [(-c|--count)] [(-s|--stat)]
            [(-d|--diff)] [--color [when]] [--no-color]
git changes (-h|--help)
git changes (-v|--version)
```

### [settings][]

Used as a compliment to `git-config` by adding missing features.

```bash
git settings get [<file-option>] [(-d|--default) <value>] <key>
git settings destroy [(-d|--dry-run)] <section>
git settings list [<file-option>] [(-p|--pretty)]
                  [(-f|--format) <format>] [(-c|--count)]
                  [(-k|--keys)] [<section>]
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
git abandon [(-d|--dry-run)] [(-q|--quiet)] [<start>] <end>
git abandon (-h|--help)
git abandon (-v|--version)
```

### [restash][]

Used to restash changes.

```bash
git restash [(-q|--quiet)] [<stash>]
git restash (-h|--help)
git restash (-v|--version)
```

### [tuck][]

Used to stash specific files rather than the all-or-nothing style of `git stash`.

```bash
git tuck [(-m|--message) <message>] [(-i|--ignore-deleted)|(-I|--no-ignore-deleted)]
         [(-q|--quiet)] -- <file> [<file> ...]
git tuck (-h|--help)
git tuck (-v|--version)
```

## Dependencies

- [colorama](https://pypi.python.org/pypi/colorama): `$ pip install colorama`

[state]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-state.1.html
[snapshot]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-snapshot.1.html
[changes]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-changes.1.html
[settings]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-settings.1.html
[upstream]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-upstream.1.html
[abandon]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-abandon.1.html
[restash]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-restash.1.html
[tuck]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-tuck.1.html
