"""List the commits between this branch and another."""

import os
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
    elif git.is_empty_repository():
        messages.error('cannot associate while empty')
    elif git.is_detached():
        messages.error('cannot associate while HEAD is detached')

    # is it a ref?
    if git.is_ref(committish):
        if not git.is_ref_ambiguous(committish, limit=('heads', 'tags')):
            committish = git.symbolic_full_name(committish)
        else:
            _ambiguous_ref(committish)
    else:
        resolved_committish = git.resolve_sha1(committish)
        if not resolved_committish:
            messages.error('{} is not a valid revision'.format(committish))
        committish = resolved_committish

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
    upstream_branch = upstream.upstream(branch, include_remote=upstream.IncludeRemote.NONE_LOCAL)
    if not upstream_branch:
        messages.error('{} has no upstream branch'.format(branch))
    associate(upstream_branch, quiet)


def _get_associated_branches():
    config_command = ('git', 'config', '--local', '--name-only', '--get-regexp', 'git-changes.associations')
    config_proc = subprocess.Popen(config_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    current_associations = config_proc.communicate()[0].splitlines()
    return [association[25:-5] for association in current_associations]  # slice off git-changes.associations. and .with


def _prune_associations(cleanup, quiet, dry_run=False):
    """Remove associations for branches that no longer exist."""

    if git.is_empty_repository():
        return

    # get branches
    current_branches = [ref.split()[1][11:] for ref in subprocess.check_output(('git', 'show-ref', '--heads')).splitlines()]

    # get associations
    current_associations = _get_associated_branches()

    branches_to_prune = current_associations
    if cleanup == 'prune':
        # remove only stale associations
        branches_to_prune = list(set(current_associations) - set(current_branches))
    for to_prune in branches_to_prune:
        if dry_run:
            messages.info('Would remove association {0!r}'.format(to_prune), quiet)
        else:
            unassociate(to_prune)
            messages.info('Removed association {0!r}'.format(to_prune), quiet)


def unassociate(branch=None, cleanup=None, quiet=False, dry_run=False):
    """Unassociate a branch.

    :param str or unicode branch: branch to unassociate
    :param str or unicode cleanup: cleanup action (one of: all, prune)
    :param bool quiet: suppress non-error output
    :param bool dry_run: show the association(s) that would be remove but do nothing
    """

    assert not cleanup or cleanup in ('all', 'prune'), 'cleanup must be one of ' + str(['all', 'prune'])

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))

    if cleanup:
        _prune_associations(cleanup, quiet, dry_run)
    else:
        branch = branch if branch else git.current_branch()
        current_association = get_association(branch)
        if current_association:
            if dry_run:
                messages.info('Would unassociate {0!r} from {1!r}'.format(branch, current_association))
            else:
                subprocess.call(['git', 'config', '--local', '--remove-section', 'git-changes.associations.' + branch])


def get_association(branch=None, verbose=False):
    """Return the associated commit-ish.

    :param str or unicode branch: the branch whose association should be returned
    :param bool verbose: print default association when none exist
    :return str or unicode: the associated commit-ish or None
    """

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))
    elif git.is_empty_repository():
        messages.warn('repository is empty')
        return None

    branch = branch if branch else git.current_branch()
    default_branch = settings.get('git-changes.default-commit-ish', default='refs/heads/master')
    if branch == 'HEAD' or not branch:
        associated_branch = None
    else:
        associated_branch = settings.get('git-changes.associations.' + branch + '.with', config='local')

    if not associated_branch and verbose:
        return default_branch
    return associated_branch


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

    color_when = git.resolve_coloring(color_when)
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
