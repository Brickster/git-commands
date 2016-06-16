"""Stash specific files."""

import os
import re
import sys
from subprocess import call, check_output

import snapshot
from utils import directories
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

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

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

    files_to_tuck = list(set(files_to_tuck))

    if not files_to_tuck:
        error("no files to tuck using")

    snapshot.snapshot(None, False)  # TODO: possibly use `git stash create`?

    # clean the working tree of any files we won't stash
    ignore_files = [':!{}'.format(f) for f in files_to_tuck]
    call(['git', 'reset', '--quiet', '--', '.'] + ignore_files)                     # reset all non-tuck files
    call(['git', 'checkout', '--quiet', '--', '.'] + ignore_files)                  # checkout all non-tuck files
    call(['git', 'clean', '--quiet', '-d', '--force', '--', '.'] + ignore_files)    # clean all non-tuck files

    # stash the files
    stash_command = ['git', 'stash', 'save', '--include-untracked']
    if message:
        stash_command += [message]
    result_message = check_output(stash_command)

    # restore the original state then clean the working tree of the files we stashed
    call(['git', 'stash', 'pop', '--quiet', '--index', 'stash@{1}'])
    call(['git', 'reset', '--quiet', '--'] + files_to_tuck)

    # checkout will complain about new files so find them and handle them accordingly
    new_files = check_output(['git', 'ls-files', '--others', '--'] + files).splitlines()
    if new_files:
        call(['git', 'checkout', '--quiet', '--'] + [x for x in files_to_tuck if x not in new_files])
        call(['git', 'clean', '--quiet', '-d', '--force', '--'] + new_files)
    else:
        call(['git', 'checkout', '--quiet', '--'] + files_to_tuck)

    info(result_message.strip(), quiet)
