"""Stash specific files."""

import os
import re
import subprocess
import sys
import uuid

import snapshot
from utils import directories, git, messages


def _status(show_color='auto'):
    return subprocess.check_output(['git', '-c', 'color.ui=' + show_color, 'status', '--short'])


def _resolve_files(files, ignore_deleted, indexed):
    if files and indexed is None:
        if not ignore_deleted:
            deleted_files = git.deleted_files()
            not_explicitly_deleted_files = [f for f in deleted_files if f not in files]
            if not_explicitly_deleted_files:
                messages.warn('deleted files exist in working tree')
                messages.warn('deleted files are not considered by pathspecs and must be added explicitly or ignored')
                messages.usage('git tuck -- PATHSPEC {}'.format(' '.join(not_explicitly_deleted_files)))
                messages.usage('git tuck --ignore-deleted -- PATHSPEC')
                sys.exit(1)

        # resolve the files to be tucked
        files_to_tuck = subprocess.check_output(['git', 'diff', '--name-only', '--cached', '--'] + files).splitlines()
        files_to_tuck += subprocess.check_output(['git', 'diff', '--name-only', '--'] + files).splitlines()

        # resolve new files to be tucked
        files_to_tuck += subprocess.check_output(['git', 'ls-files', '--others', '--'] + files).splitlines()

        files_to_tuck = list(set(files_to_tuck))
    elif not files and indexed is not None and indexed:
        files_to_tuck = subprocess.check_output(('git', 'diff', '--name-only', '--cached')).splitlines()
    elif not files and indexed is not None and not indexed:
        files_to_tuck = subprocess.check_output(('git', 'diff', '--name-only')).splitlines()
        files_to_tuck += subprocess.check_output(('git', 'ls-files', '--others')).splitlines()
    else:
        raise Exception('specifying files is not compatible with indexing option: index={}'.format(indexed))

    return files_to_tuck


def _run(files_to_tuck, message, quiet):

    if not files_to_tuck:
        messages.error('no files to tuck')

    # create a snapshot to be used later to restore the untucked files. Named uniquely to guarantee the stash will be
    # created even if it collides with a previous stash created within the last second.
    snapshot.snapshot('tuck snapshot ' + str(uuid.uuid4()), False)

    # clean the working tree of any files we won't stash
    ignore_files = [':!{}'.format(f) for f in files_to_tuck]
    subprocess.call(['git', 'reset', '--quiet', '--', '.'] + ignore_files)  # reset all non-tuck files
    subprocess.call(['git', 'checkout', '--quiet', '--', '.'] + ignore_files)  # checkout all non-tuck files
    subprocess.call(['git', 'clean', '--quiet', '-d', '--force', '--', '.'] + ignore_files)  # clean all non-tuck files

    # stash the files
    stash_command = ['git', 'stash', 'save', '--include-untracked']
    if message:
        stash_command += [message]
    result_message = subprocess.check_output(stash_command)

    # restore the original state then clean the working tree of the files we stashed
    subprocess.call(['git', 'stash', 'pop', '--quiet', '--index', 'stash@{1}'])
    subprocess.call(['git', 'reset', '--quiet', '--'] + files_to_tuck)

    # checkout will complain about new files so find them and handle them accordingly
    new_files = subprocess.check_output(['git', 'ls-files', '--others', '--'] + files_to_tuck).splitlines()
    if new_files:
        subprocess.call(['git', 'checkout', '--quiet', '--'] + [x for x in files_to_tuck if x not in new_files])
        subprocess.call(['git', 'clean', '--quiet', '-d', '--force', '--'] + new_files)
    else:
        subprocess.call(['git', 'checkout', '--quiet', '--'] + files_to_tuck)

    messages.info(result_message.strip(), quiet)


def _dry_run(files_to_tuck, show_color):

    status_output = _status(show_color)
    if files_to_tuck:
        pattern = '.*\s(?:' + '|'.join(files_to_tuck) + ')'
        tucked_output = []
        nontucked_output = []
        for line in status_output.splitlines():
            if re.search(pattern, line):
                tucked_output.append(line)
            else:
                nontucked_output.append(line)
        if not nontucked_output:
            nontucked_output.append('clean')
    elif status_output:
        tucked_output = ['nothing']
        nontucked_output = status_output.splitlines()
    else:
        messages.error('no files to tuck, the working directory is clean')

    newline_indent = os.linesep + ' ' * 4
    output = 'Would tuck:' + os.linesep
    output += newline_indent + newline_indent.join(tucked_output)
    output += os.linesep + os.linesep + 'Leaving working directory:' + os.linesep
    output += newline_indent + newline_indent.join(nontucked_output)
    output += os.linesep
    messages.info(output)


def tuck(files, indexed=None, message=None, quiet=False, ignore_deleted=False, dry_run=False, show_color='auto'):
    """Stash specific files.

    :param list files: the list of pathspecs for files to tuck
    :param bool indexed: stash indexed or non-indexed files
    :param str or unicode message: the message to use when creating the stash
    :param bool quiet: suppress non-error output
    :param bool ignore_deleted: suppress deleted file error
    :param bool dry_run: print the resulting stash and working directory but do not tuck anything
    :param str show_color: when to color output (always, never, or auto)
    """

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))

    files_to_tuck = _resolve_files(files, ignore_deleted, indexed)
    if dry_run:
        _dry_run(files_to_tuck, show_color)
    else:
        _run(files_to_tuck, message, quiet)
