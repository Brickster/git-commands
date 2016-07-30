"""Stash specific files."""

import os
import sys
from subprocess import call, check_output, PIPE, Popen

import snapshot
from utils import directories, git
from utils.messages import error, info, usage, warn


def _status(show_color='auto'):
    return check_output(['git', '-c', 'color.ui=' + show_color, 'status', '--short'])


def tuck(files, indexed=None, message=None, quiet=False, ignore_deleted=False, dry_run=False, show_color='auto'):
    """Stash specific files.

    :param list files: the list of pathspecs for files to tuck
    :param str or unicode message: the message to use when creating the stash
    :param bool quiet: suppress output
    :param bool ignore_deleted: suppress deleted file error
    """

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    if files and indexed is None:
        if not ignore_deleted:
            deleted_files = git.deleted_files()
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
    elif not files and indexed is not None and indexed:
        files_to_tuck = check_output('git diff --name-only --cached'.split()).splitlines()
    elif not files and indexed is not None and not indexed:
        files_to_tuck = check_output('git diff --name-only'.split()).splitlines()
        files_to_tuck += check_output('git ls-files --others'.split()).splitlines()
    else:
        raise Exception('specifying files is not compatible with indexing option: index={}'.format(indexed))

    if dry_run:

        status_output = _status(show_color)
        if files_to_tuck:
            tucked_output = Popen(
                ('egrep', '|'.join(files_to_tuck)),
                stdin=PIPE,
                stdout=PIPE
            ).communicate(input=status_output)[0]
            nontucked_output = Popen(
                ('egrep', '--invert-match', '|'.join(files_to_tuck)),
                stdin=PIPE,
                stdout=PIPE
            ).communicate(input=status_output)[0]
            if not nontucked_output:
                nontucked_output = 'clean'
        elif status_output:
            tucked_output = 'nothing'
            nontucked_output = status_output
        else:
            error('no files to tuck, the working directory is clean')

        newline_indent = os.linesep + ' ' * 4
        output = 'Would tuck:' + os.linesep
        output += newline_indent + newline_indent.join(tucked_output.splitlines())
        output += os.linesep + os.linesep + 'Leaving working directory:' + os.linesep
        output += newline_indent + newline_indent.join(nontucked_output.splitlines())
        output += os.linesep
        info(output)

    else:

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
        new_files = check_output(['git', 'ls-files', '--others', '--'] + files_to_tuck).splitlines()
        if new_files:
            call(['git', 'checkout', '--quiet', '--'] + [x for x in files_to_tuck if x not in new_files])
            call(['git', 'clean', '--quiet', '-d', '--force', '--'] + new_files)
        else:
            call(['git', 'checkout', '--quiet', '--'] + files_to_tuck)

        info(result_message.strip(), quiet)
