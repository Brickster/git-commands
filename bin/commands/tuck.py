"""Stash specific files."""

import re
import sys
from subprocess import call, check_output

from utils import git
from utils.messages import error, info, usage, warn


def _deleted_files():
    """Get the deleted files in a dirty working tree.

    :return list: a list of deleted file paths
    """

    all_files = check_output(['git', 'status', '--short', '--porcelain'])
    return [match.group(1) for match in re.finditer('^(?:D\s|\sD)\s(.*)', all_files, re.MULTILINE)]


def tuck(files, message=None, quiet=False, ignore_deleted=False):
    """Stash specific files.

    :param list files: the list of pathspecs for files to tuck
    :param str or unicode message: the message to use when creating the stash
    :param bool quiet: suppress output
    :param bool ignore_deleted: suppress deleted file error
    """

    if not ignore_deleted:
        deleted_files = _deleted_files()
        not_explicitly_deleted_files = [f for f in deleted_files if f not in files]
        if not_explicitly_deleted_files:
            warn('deleted files exist in working tree')
            warn('deleted files are not considered by pathspecs and must be added explicitly or ignored')
            usage('git tuck -- PATHSPEC {}'.format(' '.join(not_explicitly_deleted_files)))
            usage('git tuck --ignore-deleted -- PATHSPEC')
            sys.exit(1)

    # resolve the files to be tucked
    files_to_tuck = check_output(['git', 'diff', '--name-only', '--cached', '--'] + files).splitlines()
    files_to_tuck += check_output(['git', 'diff', '--name-only', '--'] + files).splitlines()

    # resolve new files to be tucked
    files_to_tuck += check_output(['git', 'ls-files', '--others', '--'] + files).splitlines()

    if not files_to_tuck:
        error("no files to tuck using")

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

    # the default stash message includes the HEAD commit and won't look right if the intermediate commit is used
    current_branch = git.current_branch()
    temp_branch = current_branch + '-tmp'
    call(['git', 'branch', '--move', temp_branch])
    checkout_command = ['git', 'checkout', '--quiet', '-b', current_branch]
    if unstaged and staged:
        call(checkout_command + ['HEAD^^'])
    elif unstaged or staged:
        call(checkout_command + ['HEAD^'])
    else:
        call(checkout_command)  # TODO: this isn't necessary and should be refactored

    # stash files to be tucked
    stash_command = ['git', 'stash', 'save', '--include-untracked']
    if message:
        stash_command += [message]
    result_message = check_output(stash_command)
    call(['git', 'checkout', '--quiet', '-B', current_branch, temp_branch])
    call(['git', 'branch', '--quiet', '-D', temp_branch])

    # if message:
    #     stash_command += [message]
    #     result_message = check_output(stash_command)
    # else:
    #     # the default stash message includes the HEAD commit and won't look right if the intermediate commit is used
    #     current_branch = git.current_branch()
    #     temp_branch = current_branch + '-tmp'
    #     call(['git', 'branch', '--move', temp_branch])
    #     checkout_command = ['git', 'checkout', '--quiet', '-b', current_branch]
    #     if unstaged and staged:
    #         call(checkout_command + ['HEAD^^'])
    #     elif unstaged or staged:
    #         call(checkout_command + ['HEAD^'])
    #     else:
    #         call(checkout_command)  # TODO: this isn't necessary and should be refactored
    #     result_message = check_output(stash_command)
    #     call(['git', 'checkout', '--quiet', '-B', current_branch, temp_branch])
    #     call(['git', 'branch', '--quiet', '-D', temp_branch])

    # reset all original files
    reset_command = ['git', 'reset', '--quiet', 'HEAD^']
    if unstaged:
        call(reset_command)
    if staged:
        call(reset_command + ['--soft'])

    info(result_message.strip(), quiet)
