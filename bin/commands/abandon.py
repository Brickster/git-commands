"""Drop a count or range of stashes."""

from subprocess import call, check_output

from utils.messages import error


def abandon(start, end, dry_run=False):
    """Drop a range of stashes from start (inclusive) to end (exclusive)."""

    stash_count = len(check_output(['git', 'stash', 'list']).splitlines())
    if end < start:
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
            print 'Would drop refs/{} ({})'.format(stash, stash_sha)
    else:
        start_stash = 'stash@{{{}}}'.format(start)
        for i in range(start, end):
            stash_sha = check_output(['git', 'rev-parse', start_stash]).splitlines()[0]
            call(['git', 'stash', 'drop', '--quiet', start_stash])
            print 'Dropped refs/stash@{{{}}} ({})'.format(i, stash_sha)
