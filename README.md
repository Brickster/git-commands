# git-commands

A collection of custom git commands

## state

Used to see a more concise and comprehensive view of the working directory. The output includes results from git status, git log, and git branch.

```bash
git state [(-h|--help)] [(-l|--log) <count>] [(-L|--no-log)] [--full-log] [(-S|--no-status)] [(-B|--no-branches)] [(-T|--no-stashes)] [(-e|--show-empty)] [(-c|--color)] [(-C|--no-color)] [(-p|--pretty)]
```

## snapshot

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

## changes

Used to list the commits between this branch and another.

```bash
git changes [(-b|--branch) <branch>] [(-c|--count)] [(-h|--help)]
```

## settings

Used as a compliment to `git-config` by adding missing features.

```bash
git-settings [(-h|--help)]  
git-settings [(--local|--global|--system)] --destroy-section <section>  
git-settings [(--local|--global|--system)] --print-section <section>
```
