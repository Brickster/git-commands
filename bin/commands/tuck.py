"""Stash specific files."""

import re
import sys
from subprocess import call, check_output

from utils.messages import error, info, usage, warn


def _deleted_files():
    """Get the deleted files in a dirty working tree."""

    all_files = check_output(['git', 'status', '--short', '--porcelain'])
    return [match.group(1) for match in re.finditer('^(?:D\s|\sD)\s(.*)', all_files, re.MULTILINE)]


def tuck(files, message=None, quiet=False, ignore_deleted=False):
    """Stash specific files."""

    if not ignore_deleted:
        deleted_files = _deleted_files()
        not_explicitly_deleted_files = [f for f in deleted_files if f not in files]
        if not_explicitly_deleted_files:
            warn('deleted files exist in working tree')
            warn('deleted files are not considered by pathspec and must be added explicitly or ignored')
            usage('git tuck -- <pathspec> {}'.format(' '.join(not_explicitly_deleted_files)))
            usage('git tuck --ignore-deleted -- <pathspac>')
            sys.exit(1)

    # resolve the files to be tucked
    files_to_tuck = check_output(['git', 'diff', '--name-only', '--cached', '--'] + files).splitlines()
    files_to_tuck += check_output(['git', 'diff', '--name-only', '--'] + files).splitlines()

    # resolve new files to be tucked
    files_to_tuck += check_output(['git', 'ls-files', '--others', '--'] + files).splitlines()

    if not files_to_tuck:
        error("no files to tuck using: " + ' '.join(files))

    # reset the files to be tucked in the event they have changes. Like stash, we won't keep track of staged/unstaged
    # changes
    call(['git', 'reset', '--quiet', '--'] + files_to_tuck)

    # commit already staged files
    staged = check_output('git diff --name-only --cached'.split())
    if staged:
        check_output(['git', 'commit', '--message', 'TUCK: staged', '--quiet']).splitlines()

    # commit unstaged files
    ignore_files = [':!{}'.format(f) for f in files_to_tuck]
    call(['git', 'add', '--', '.'] + ignore_files)
    unstaged = check_output('git diff --name-only --cached'.split())
    if unstaged:
        call(['git', 'commit', '--message', 'TUCK: unstaged', '--quiet'])

    # stash files to be tucked
    stash_command = ['git', 'stash', 'save', '--include-untracked', '--quiet']
    if message:
        stash_command += [message]
    check_output(stash_command)

    # reset all original files
    reset_command = ['git', 'reset', '--quiet', 'HEAD^']
    if unstaged:
        call(reset_command)
    if staged:
        call(reset_command + ['--soft'])

    info('Tucked files: ' + ' '.join(files_to_tuck), quiet)
