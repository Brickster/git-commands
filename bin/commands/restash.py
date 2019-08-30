"""Restash changes."""

import re

from utils import execute, messages


def _is_valid_stash(stash):
    """Determines if a stash reference is valid.

    :param str or unicode stash: a stash reference

    :return bool: whether or not the stash is valid
    """

    if re.match('^stash@{.*}$', stash) is None:
        return False
    return execute.swallow(['git', 'cat-file', '-t', stash]) == 0


def _parents(commit):
    """Returns the parents of a commit.

    :param str or unicode commit: a commit to find parents of

    :return list: a list of parent SHAs
    """

    return execute.check_output(['git', 'rev-list', '--parents', '-1', commit]).strip().split(' ')[1:]


def restash(stash='stash@{0}', quiet=False):
    """Restash a stash reference.

    :param str or unicode stash: stash reference to reverse apply
    :param bool quiet: suppress all output
    """

    if not execute.check_output('git stash list'):
        messages.error('no stashes exist')
    if not _is_valid_stash(stash):
        messages.error('{} is not a valid stash reference'.format(stash))

    _reverse_modifications(stash)
    _remove_untracked_files(stash)

    stash_sha = execute.check_output(['git', 'rev-parse', stash]).splitlines()[0]
    messages.info('Restashed {} ({})'.format(stash, stash_sha), quiet)


def _reverse_modifications(stash):
    # if there are modifications, reverse apply them
    reverse_patch = execute.check_output(['git', 'stash', 'show', '--patch', '--no-color', stash])
    if reverse_patch:
        return_code = execute.call_input(['git', 'apply', '--reverse'], reverse_patch)
        if return_code:
            messages.error('unable to reverse modifications', exit_=True)


def _remove_untracked_files(stash):
    # check if we need remove any untracked files. For a stash ref, the third parent contains the untracked files.
    parents = _parents(stash)
    if len(parents) == 3:
        untracked_files = execute.check_output(['git', 'ls-tree', '--name-only', '{}^3'.format(stash)]).splitlines()

        # it's possible to have three parents and no untracked files if --include-untracked was unnecessarily used
        if untracked_files:
            execute.call(['git', 'clean', '--force', '--quiet', '--'] + untracked_files)
