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


def unassociate(branch=git.current_branch(), all=False):
    """Unassociate a branch.

    :param str or unicode branch: branch to unassociate
    :param bool all: unassociate all branches
    """

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    if all:
        with open(os.devnull, 'w') as devnull:
            call(('git', 'config', '--local', '--remove-section', 'git-changes.associations'), stdout=devnull, stderr=STDOUT)
    else:
        call(['git', 'config', '--local', '--unset', 'git-changes.associations.' + branch])


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
