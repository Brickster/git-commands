"""Drop a count or range of stashes."""

from .utils import execute, messages


def abandon(start: int, end: int, dry_run: bool = False, quiet: bool = False) -> None:
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


def _dry_run(start: int, end: int) -> None:
    for i in range(start, end):
        stash = f'stash@{{{i}}}'
        stash_sha = execute.check_output(['git', 'rev-parse', stash]).splitlines()[0]
        messages.info(f'Would drop refs/{stash} ({stash_sha})')


def _run(start: int, end: int, quiet: bool) -> None:
    start_stash = f'stash@{{{start}}}'
    for i in range(start, end):
        stash_sha = execute.check_output(['git', 'rev-parse', start_stash]).splitlines()[0]
        execute.call(['git', 'stash', 'drop', '--quiet', start_stash])
        messages.info(f'Dropped refs/stash@{{{i}}} ({stash_sha})', quiet)


def _validate_bounds(start: int, end: int) -> tuple[int, int]:
    stash_count = len(execute.check_output(['git', 'stash', 'list']).splitlines())
    if end < 0:
        messages.error('end cannot be negative')
    elif end < start:
        messages.error('end of range cannot come before the start')
    elif start > stash_count:
        messages.error('start too high', exit_=False)
        messages.error(f'only {stash_count} stashes exist')
    elif end > stash_count:
        end = stash_count
    return start, end
