# git-commands

A collection of custom git commands

## [state](http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-state.1.html)

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

## [snapshot](http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-snapshot.1.html)

Used to record the current state of the working directory without reverting it. The snapshot is stored using git stash prepended with snapshot@{i} to differentiate it and stashes created normally.

```bash
git snapshot [(-h|--help)]
git snapshot save <message>
git snapshot list
git snapshot clear
git snapshot drop <snapshot>
git snapshot apply <snapshot>
git snapshot pop <snapshot>
git snapshot show <snapshot>
```

## [changes](http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-changes.1.html)

Used to list the commits between this branch and another.

```bash
git changes [(-b|--branch) <branch>] [(-c|--count)]
git changes [(-h|--help)]
```

## [settings](http://htmlpreview.github.io/?https://raw.githubusercontent.com/Brickstertwo/git-commands/master/man/man1/git-settings.1.html)

Used as a compliment to `git-config` by adding missing features.

```bash
git settings [<file-option>] [(-d|--default) <value>] <key>
git settings [(-h|--help)]
git settings destroy [<file-option>] <section>
git settings print [<file-option>] [(-p|--pretty)] [(-f|--format) <format>] [(-c|--count)] <section>
git settings list
```
