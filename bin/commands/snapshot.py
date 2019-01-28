"""Create a snapshot of the changes in a dirty working directory."""

import subprocess
import time

from utils import execute, messages


def _stash_buffer(quiet):
    """
    You cannot create two stashes of the same contents within the same second. So wait if we've executed too quickly.
    """

    # TODO: this should check that the stash would be a duplicate first
    if subprocess.check_output(('git', 'stash', 'list')).strip():
        last_stash_date = subprocess.check_output(('git', 'show', '-s', '--format=%ci', 'stash@{0}')).rstrip()
        warned = False
        while last_stash_date == time.strftime('%Y-%m-%d %H:%M:%S %z'):
            warned = messages.warn('snapshot created too close to last stash', quiet=quiet, ignore=warned)
            time.sleep(0.1)


def snapshot(message=None, quiet=False, files=None):
    """Create a snapshot of the working directory and index.

    :param str or unicode message: the message to use when creating the underlying stash
    :param bool quiet: suppress all output
    :param list files: a list of pathspecs to specific files to use when creating the snapshot
    """

    status_command = ['git', 'status', '--porcelain']
    status_output = subprocess.check_output(status_command).splitlines()

    # if there aren't any changes then we don't have anything to do
    if not status_output:
        messages.info('No local changes to save. No snapshot created.', quiet)
        return

    stash_command = ['git', 'stash', 'push', '--include-untracked', '--quiet']
    stash_command = stash_command if message is None else stash_command + ['--message', message]
    stash_command = stash_command if not files else stash_command + ['--'] + files
    _stash_buffer(quiet)
    subprocess.call(stash_command)

    # apply isn't completely quiet when the stash only contains untracked files so swallow all output
    execute.swallow(['git', 'stash', 'apply', '--quiet', '--index'])
