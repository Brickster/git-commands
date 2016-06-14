"""Drop a count or range of stashes."""

import os
from subprocess import call, check_output

from utils import directories
from utils.messages import error, info


def abandon(start, end, dry_run=False, quiet=False):
    """Drop a range of stashes from start (inclusive) to end (exclusive).

    :param int start: the range start (inclusive) of stashes to drop
    :param int end: the range end (exclusive) of stashes to drop
    :param bool dry_run: print the stashes that would be dropped but don't drop them
    :param bool quiet: suppress all output
    """

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    stash_count = len(check_output(['git', 'stash', 'list']).splitlines())
    if end < 0:
        error('end cannot be negative')
    elif end < start:
        error('end of range cannot come before the start')
    elif start > stash_count:
        error('start too high', exit=False)
        error('only {} stashes exist'.format(stash_count))
    elif end > stash_count:
        end = stash_count

    if dry_run:
        for i in range(start, end):
            stash = 'stash@{{{}}}'.format(i)
            stash_sha = check_output(['git', 'rev-parse', stash]).splitlines()[0]
            info('Would drop refs/{} ({})'.format(stash, stash_sha))
    else:
        start_stash = 'stash@{{{}}}'.format(start)
        for i in range(start, end):
            stash_sha = check_output(['git', 'rev-parse', start_stash]).splitlines()[0]
            call(['git', 'stash', 'drop', '--quiet', start_stash])
            info('Dropped refs/stash@{{{}}} ({})'.format(i, stash_sha), quiet)
