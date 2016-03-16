"""Restash changes."""

import os
import re
from subprocess import call, check_output, PIPE, Popen

from utils import directories
from utils.messages import error, info


def _is_valid_stash(stash):
    """Determines if a stash reference is valid.

    :param str or unicode stash: a stash reference

    :return bool: whether or not the stash is valid
    """

    if re.match('^stash@{.*}$', stash) is None:
        return False

    with open(os.devnull, 'w') as devnull:
        proc = Popen(('git', 'cat-file', '-t', stash), stdout=devnull, stderr=devnull)
        proc.wait()
        return proc.returncode == 0


def _parents(commit):
    """Returns the parents of a commit.

    :param str or unicode commit: a commit to find parents of

    :return list: a list of parent SHAs
    """

    return check_output(['git', 'rev-list', '--parents', '-1', commit]).strip().split(' ')[1:]


def restash(stash='stash@{0}', quiet=False):
    """Restash a stash reference.

    :param str or unicode stash: stash reference to reverse apply
    :param bool quiet: suppress all output
    """

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    if not _is_valid_stash(stash):
        error('{} is not a valid stash reference'.format(stash))

    # if there are modifications, reverse apply them
    reverse_patch = check_output(['git', 'stash', 'show', '--patch', '--no-color', stash])
    if reverse_patch:
        restash_proc = Popen(['git', 'apply', '--reverse'], stdin=PIPE)
        restash_proc.communicate(input=reverse_patch)

        if restash_proc.returncode:
            error('unable to reverse modifications', exit=True)

    # check if we need remove any untracked files. For a stash ref, the third parent contains the untracked files
    parents = _parents(stash)
    if len(parents) == 3:
        untracked_files = check_output(['git', 'ls-tree', '--name-only', '{}^3'.format(stash)]).splitlines()
        if untracked_files:
            call(['git', 'clean', '--force', '--quiet', '--'] + untracked_files)

    stash_sha = check_output(['git', 'rev-parse', stash]).splitlines()[0]
    info('Restashed {} ({})'.format(stash, stash_sha), quiet)
