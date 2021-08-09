"""Drop a count or range of stashes."""

from __future__ import absolute_import

from .utils import execute, messages


def abandon(start, end, dry_run=False, quiet=False):
    """Drop a range of stashes from start (inclusive) to end (exclusive).

    :param int start: the range start (inclusive) of stashes to drop
    :param int end: the range end (exclusive) of stashes to drop
    :param bool dry_run: print the stashes that would be dropped but don't drop them
    :param bool quiet: suppress all output
    """

    start, end = _validate_bounds(start, end)
    if dry_run:
        _dry_run(start, end)
    else:
        _run(start, end, quiet)


def _dry_run(start, end):
    for i in range(start, end):
        stash = 'stash@{{{}}}'.format(i)
        stash_sha = execute.check_output(['git', 'rev-parse', stash]).splitlines()[0]
        messages.info('Would drop refs/{} ({})'.format(stash, stash_sha))


def _run(start, end, quiet):
    start_stash = 'stash@{{{}}}'.format(start)
    for i in range(start, end):
        stash_sha = execute.check_output(['git', 'rev-parse', start_stash]).splitlines()[0]
        execute.call(['git', 'stash', 'drop', '--quiet', start_stash])
        messages.info('Dropped refs/stash@{{{}}} ({})'.format(i, stash_sha), quiet)


def _validate_bounds(start, end):
    stash_count = len(execute.check_output(['git', 'stash', 'list']).splitlines())
    if end < 0:
        messages.error('end cannot be negative')
    elif end < start:
        messages.error('end of range cannot come before the start')
    elif start > stash_count:
        messages.error('start too high', exit_=False)
        messages.error('only {} stashes exist'.format(stash_count))
    elif end > stash_count:
        end = stash_count
    return start, end
