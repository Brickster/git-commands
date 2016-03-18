"""List the commits between this branch and another."""

import os
import sys
from subprocess import call, check_output, STDOUT

from . import settings
from utils import directories, git
from utils.messages import error, info


def associate(branch):
    """Associate branches."""

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    current_branch = git.current_branch()
    call(['git', 'config', '--local', 'git-changes.associations.' + current_branch, branch])
    info('{} has been associated with {}'.format(current_branch, branch))


def _prune_associations():
    """Remove associations for branches that no longer exist."""

    # get branches
    current_branches = [ref.split()[1][11:] for ref in check_output(('git', 'show-ref', '--heads')).splitlines()]

    # get associations
    current_associations = check_output(('git', 'config', '--local', '--name-only', '--get-regexp', 'git-changes.associations')).splitlines()
    current_associations = [association[25:] for association in current_associations]

    # remove stale associations
    stale_associations = list(set(current_associations) - set(current_branches))
    for stale_association in stale_associations:
        unassociate(stale_association)
        info('Removed association {0!r}'.format(stale_association))


def unassociate(branch=git.current_branch(), cleanup=None):
    """Unassociate a branch.

    :param str or unicode branch: branch to unassociate
    :param str or unicode cleanup: cleanup action (one of: all, prune)
    """

    assert not cleanup or cleanup in ('all', 'prune'), 'cleanup must be one of ' + str(['all', 'prune'])

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    if not cleanup:
        call(['git', 'config', '--local', '--unset', 'git-changes.associations.' + branch])
    elif cleanup == 'all':
        with open(os.devnull, 'w') as devnull:
            call(('git', 'config', '--local', '--remove-section', 'git-changes.associations'), stdout=devnull, stderr=STDOUT)
    else:
        _prune_associations()


def get_association(branch=git.current_branch()):
    """Return the associated branch.

    :param str or unicode branch: the branch whose association should be returned
    :return str or unicode: the associated branch or None
    """

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))
    return settings.get('git-changes.associations.' + branch, config='local')


def changes(branch, details=None, color_when='auto'):
    """Print the changes between a given branch and HEAD"""

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))
    elif not git.is_valid_reference(branch):
        error('{0!r} is not a valid branch'.format(branch))

    color_when = color_when.lower()
    if color_when == 'never' or (color_when == 'auto' and not sys.stdout.isatty()):
        color_when = 'never'
    elif color_when == 'auto' and sys.stdout.isatty():
        color_when = 'always'

    if details == 'diff':
        call(['git', 'diff', '--color={}'.format(color_when), branch, 'HEAD'])
    elif details == 'stat':
        call(['git', 'diff', '--color={}'.format(color_when), '--stat', branch, 'HEAD'])
    else:
        command = ['git', 'log', '--oneline', '{}..HEAD'.format(branch)]
        if details == 'count':
            log = check_output(command)
            log = log.splitlines()
            info(len(log))
        else:
            command += ['--color={}'.format(color_when)]
            call(command)
