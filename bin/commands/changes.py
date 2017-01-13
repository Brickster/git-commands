"""List the commits between this branch and another."""

import os
import sys
import subprocess

from . import settings, upstream
from utils import directories, git, messages

_DETAIL_OPTIONS = ('diff', 'stat', 'count')
_COLOR_OPTIONS = ('always', 'auto', 'never')


def _ambiguous_ref(ref):
    ref_names = [r.split(' ')[1] for r in subprocess.check_output(('git', 'show-ref', '--tags', '--heads', ref)).splitlines()]
    messages.error('{0!r} is an ambiguous ref. Use one of:\n{1}'.format(ref, '\n'.join(ref_names)))


def associate(committish, quiet=False):
    """Associate the current branch with a commit-ish.

    :param str or unicode committish: the commit-ish to associate the current branch with
    :param bool quiet: suppress non-error output
    """

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))

    # is it a ref?
    if git.is_ref(committish):
        if not git.is_ref_ambiguous(committish, limit=('heads', 'tags')):
            committish = git.symbolic_full_name(committish)
        else:
            _ambiguous_ref(committish)
    else:
        committish = git.resolve_sha1(committish)

    current_branch = git.current_branch()
    subprocess.call(['git', 'config', '--local', 'git-changes.associations.' + current_branch + '.with', committish])
    messages.info('{} has been associated with {}'.format(current_branch, committish), quiet)


def associate_upstream(quiet=False):
    """Associate the current branch with its upstream branch.

    :param bool quiet: suppress non-error output
    """

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))

    branch = git.current_branch()
    upstream_branch = upstream.upstream(branch, include_remote=True)
    if not upstream_branch:
        messages.error('{} has no upstream branch'.format(branch))
    associate(upstream_branch, quiet)


def _prune_associations(cleanup, quiet):
    """Remove associations for branches that no longer exist."""

    # get branches
    current_branches = [ref.split()[1][11:] for ref in subprocess.check_output(('git', 'show-ref', '--heads')).splitlines()]

    # get associations
    current_associations = subprocess.check_output(('git', 'config', '--local', '--name-only', '--get-regexp', 'git-changes.associations')).splitlines()
    current_associations = [association[25:-5] for association in current_associations]

    branches_to_prune = current_associations
    if cleanup == 'prune':
        # remove only stale associations
        branches_to_prune = list(set(current_associations) - set(current_branches))
    for to_prune in branches_to_prune:
        unassociate(to_prune)
        messages.info('Removed association {0!r}'.format(to_prune), quiet)


def unassociate(branch=None, cleanup=None, quiet=False):
    """Unassociate a branch.

    :param str or unicode branch: branch to unassociate
    :param str or unicode cleanup: cleanup action (one of: all, prune)
    :param bool quiet: suppress non-error output
    """

    assert not cleanup or cleanup in ('all', 'prune'), 'cleanup must be one of ' + str(['all', 'prune'])

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))

    if cleanup:
        _prune_associations(cleanup, quiet)
    else:
        branch = branch if branch else git.current_branch()
        subprocess.call(['git', 'config', '--local', '--remove-section', 'git-changes.associations.' + branch])


def get_association(branch=None):
    """Return the associated commit-ish.

    :param str or unicode branch: the branch whose association should be returned
    :return str or unicode: the associated commit-ish or None
    """

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))
    branch = branch if branch else git.current_branch()
    return settings.get('git-changes.associations.' + branch + '.with', config='local')


def changes(committish, details=None, color_when=None):
    """Print the changes between a given branch and HEAD.

    :param str or unicode committish: commit-ish to view changes from
    :param str or unicode details: the level of details to show (diff, stat, or None)
    :param str or unicode color_when: when to color output
    """

    assert not details or details in _DETAIL_OPTIONS, 'details must be one of ' + str(_DETAIL_OPTIONS)
    assert not color_when or color_when in _COLOR_OPTIONS, 'color_when must be one of ' + str(_COLOR_OPTIONS)

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))
    elif not git.is_commit(committish):
        messages.error('{0!r} is not a valid commit'.format(committish))
    elif git.is_ref(committish) and git.is_ref_ambiguous(committish, limit=('heads', 'tags')):
        _ambiguous_ref(committish)

    color_when = color_when.lower() if color_when else settings.get('color.ui', default='auto')
    if color_when == 'never' or (color_when == 'auto' and not sys.stdout.isatty()):
        color_when = 'never'
    elif color_when == 'auto' and sys.stdout.isatty():
        color_when = 'always'

    if details == 'diff':
        subprocess.call(['git', 'diff', '--color={}'.format(color_when), committish + '...HEAD'])
    elif details == 'stat':
        subprocess.call(['git', 'diff', '--color={}'.format(color_when), '--stat', committish + '...HEAD'])
    else:
        command = ['git', 'log', '--oneline', '{}..HEAD'.format(committish)]
        if details == 'count':
            log = subprocess.check_output(command)
            log = log.splitlines()
            messages.info(str(len(log)))
        else:
            command += ['--color={}'.format(color_when)]
            subprocess.call(command)
