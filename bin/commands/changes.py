"""List the commits between this branch and another."""

from __future__ import absolute_import

import os

from enum import Enum

from . import upstream
from .utils import directories, execute, git, messages


class DetailsOption(Enum):
    LOG = 1,
    INVERSE_LOG = 2,
    DIFF = 3,
    STAT = 4,
    COUNT = 4


class ColorOption(Enum):
    ALWAYS = 1,
    AUTO = 2,
    NEVER = 3


class CleanupOption(Enum):
    ALL = 1,
    PRUNE = 2


def _ambiguous_ref(ref):
    ref_names = [r.split(' ')[1] for r in execute.check_output(['git', 'show-ref', '--tags', '--heads', ref]).splitlines()]
    messages.error("'{0}' is an ambiguous ref. Use one of:\n{1}".format(ref, '\n'.join(ref_names)))


def associate(committish, quiet=False):
    """Associate the current branch with a commit-ish.

    :param str or unicode committish: the commit-ish to associate the current branch with
    :param bool quiet: suppress non-error output
    """

    if not directories.is_git_repository():
        messages.error("'{}' not a git repository".format(os.getcwd()))
    elif git.is_empty_repository():
        messages.error('cannot associate while empty')
    elif git.is_detached():
        messages.error('cannot associate while HEAD is detached')

    # is it a ref?
    if git.is_ref(committish):
        if not git.is_ref_ambiguous(committish, limit=(git.RefType.HEADS, git.RefType.TAGS)):
            committish = git.symbolic_full_name(committish)
        else:
            _ambiguous_ref(committish)
    else:
        resolved_committish = git.resolve_sha1(committish)
        if not resolved_committish:
            messages.error('{} is not a valid revision'.format(committish))
        committish = resolved_committish

    current_branch = git.current_branch()
    execute.call(['git', 'config', '--local', 'git-changes.associations.' + current_branch + '.with', committish])
    messages.info('{} has been associated with {}'.format(current_branch, committish), quiet)


def associate_upstream(quiet=False):
    """Associate the current branch with its upstream branch.

    :param bool quiet: suppress non-error output
    """

    if not directories.is_git_repository():
        messages.error("'{}' not a git repository".format(os.getcwd()))

    branch = git.current_branch()
    upstream_branch = upstream.upstream(branch, include_remote=upstream.IncludeRemote.NONE_LOCAL)
    if not upstream_branch:
        messages.error('{} has no upstream branch'.format(branch))
    associate(upstream_branch, quiet)


def _get_associated_branches():
    current_associations = execute.stdout(
        'git config --local --name-only --get-regexp git-changes.associations'
    ).splitlines()
    return [association[25:-5] for association in current_associations]  # slice off git-changes.associations. and .with


def _prune_associations(cleanup, quiet, dry_run=False):
    """Remove associations for branches that no longer exist."""

    # get branches and associations
    current_branches = [ref.split()[1][11:] for ref in execute.check_output('git show-ref --heads').splitlines()]
    current_associations = _get_associated_branches()

    branches_to_prune = current_associations
    if cleanup == CleanupOption.PRUNE:
        # remove only stale associations
        branches_to_prune = list(set(current_associations) - set(current_branches))
    for to_prune in branches_to_prune:
        if dry_run:
            messages.info("Would remove association '{}'".format(to_prune), quiet)
        else:
            unassociate(to_prune)
            messages.info("Removed association '{}'".format(to_prune), quiet)


def unassociate(branch=None, cleanup=None, quiet=False, dry_run=False):
    """Unassociate a branch.

    :param str or unicode branch: branch to unassociate
    :param CleanupOption cleanup: cleanup action
    :param bool quiet: suppress non-error output
    :param bool dry_run: show the association(s) that would be remove but do nothing
    """

    if not directories.is_git_repository():
        messages.error("'{}' not a git repository".format(os.getcwd()))
    elif git.is_empty_repository():
        return

    if cleanup:
        _prune_associations(cleanup, quiet, dry_run)
    else:
        branch = branch if branch else git.current_branch()
        current_association = get_association(branch)
        if current_association:
            if dry_run:
                messages.info("Would unassociate '{0}' from '{1}'".format(branch, current_association))
            else:
                execute.call(['git', 'config', '--local', '--remove-section', 'git-changes.associations.' + branch])


def get_association(branch=None, verbose=False):
    """Return the associated commit-ish.

    :param str or unicode branch: the branch whose association should be returned
    :param bool verbose: print default association when none exist
    :return str or unicode: the associated commit-ish or None
    """

    if not directories.is_git_repository():
        messages.error("'{}' not a git repository".format(os.getcwd()))
    elif git.is_empty_repository():
        messages.warn('repository is empty')
        return None

    branch = branch if branch else git.current_branch()
    associated_branch = _resolve_association(branch)

    if not associated_branch and verbose:
        return git.get_config_value('git-changes.default-commit-ish', default='refs/heads/master')
    return associated_branch


def _resolve_association(branch):
    if branch == 'HEAD' or not branch:
        associated_branch = None
    else:
        associated_branch = git.get_config_value('git-changes.associations.' + branch + '.with', config='local')
    return associated_branch


def changes(committish, details=None, color_when=None, files=None):
    """Print the changes between a given branch and HEAD.

    :param str or unicode committish: commit-ish to view changes from
    :param DetailsOption details: the level of details to show
    :param ColorOption color_when: when to color output
    :param list files: a list of pathspecs to specific files
    """

    if not directories.is_git_repository():
        messages.error("'{}' not a git repository".format(os.getcwd()))
    elif not git.is_commit(committish):
        messages.error("'{}' is not a valid commit".format(committish))
    elif git.is_ref(committish) and git.is_ref_ambiguous(committish, limit=(git.RefType.HEADS, git.RefType.TAGS)):
        _ambiguous_ref(committish)

    if details and isinstance(details, str):
        details = DetailsOption[details.upper()]
    if color_when and isinstance(color_when, str):
        color_when = ColorOption[color_when.upper()]
    color_when = git.resolve_coloring(color_when.name if color_when is not None else None)

    _print_changes(committish, details, color_when, files)


def _print_changes(committish, details, color_when, files):
    if details == DetailsOption.DIFF:
        command = ['git', 'diff', '--color={}'.format(color_when), committish + '...HEAD']
        execute.call(_append_any_file_args(command, files))
    elif details == DetailsOption.STAT:
        command = ['git', 'diff', '--color={}'.format(color_when), '--stat', committish + '...HEAD']
        execute.call(_append_any_file_args(command, files))
    elif details == DetailsOption.COUNT:
        command = ['git', 'log', '--no-decorate', '--oneline', '{}..HEAD'.format(committish)]
        log = execute.check_output(_append_any_file_args(command, files))
        log = log.splitlines()
        messages.info(str(len(log)))
    elif details == DetailsOption.INVERSE_LOG:
        merge_base = execute.check_output(['git', 'merge-base', committish, 'HEAD']).strip()
        # TODO: make length configurable
        command = ['git', 'log', '--no-decorate', '--oneline', '-10', merge_base, '--color={}'.format(color_when)]
        execute.call(_append_any_file_args(command, files))
    else:
        command = [
            'git', 'log', '--no-decorate', '--oneline', '{}..HEAD'.format(committish), '--color={}'.format(color_when)
        ]
        execute.call(_append_any_file_args(command, files))


def _append_any_file_args(command, files):
    if files:
        command += ['--', ' '.join(files)]
    return command
