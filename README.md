# git-commands

A collection of custom git commands

## state

Used to see a more concise and comprehensive view of the working directory. The output includes results from git status, git log, and git branch.

```bash
git state [(-h|--help)] [(-l|--log) <count>] [--no-log] [--no-status] [--no-branches] [--no-stashes]
```

## snapshot

Used to record the current state of the working directory without reverting it. The snapshot is stored using git stash prepended with snapshot@{i} to differentiate it and stashes created normally.

```bash
git snapshot [(-m|--message) <message>] [(-h|--help)]
git snapshot list
git snapshot clear
git snapshot delete <snapshot>
```
