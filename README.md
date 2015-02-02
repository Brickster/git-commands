# git-commands

A collection of custom git commands

## Install

```bash
make [install]
```
```bash
export PATH="$PATH:/path/to/git-commands/repository/bin"
```

## Uninstall

```bash
make uninstall
```
```bash
# remote the preveously added line
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
          [(-c|--color)] [(-C|--no-color)]
          [(-p|--pretty)] [(-f|--format) <format>]
git state [(-h|--help)]
```

### [snapshot][]

Used to record the current state of the working directory without reverting it.

```bash
git snapshot <message>
git snapshot [(-h|--help)]
```

### [changes][]

Used to list the commits between this branch and another.

```bash
git changes [(-b|--branch) <branch>] [(-c|--count)]
git changes [(-h|--help)]
```

### [settings][]

Used as a compliment to `git-config` by adding missing features.

```bash
git settings [<file-option>] [(-d|--default) <value>] <key>
git settings [(-h|--help)]
git settings destroy [(-d|--dry-run)] <section>
git settings list
git settings list [<file-option>] [(-p|--pretty)] [(-f|--format) <format>] [(-c|--count)] <section>
```

### [upstream][]

Used to get the current upstream branch.

```bash
git upstream [(-r|--include-remote)] [(-R|--no-include-remote)]
git upstream [(-h|--help)]
```

### [fixup][]

Used as a shortcut for committing the currently staged files as an autosquashable fixup.

```bash
git fixup [(-b|--message-body) <message-body>] [<commit>]
git fixup [(-h|--help)]
```

[state]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-state.1.html
[snapshot]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-snapshot.1.html
[changes]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-changes.1.html
[settings]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-settings.1.html
[upstream]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-upstream.1.html
[fixup]: http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-fixup.1.html
