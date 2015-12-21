"""Create a snapshot of the changes in a dirty working directory."""

import os
from subprocess import call, check_output, STDOUT

from utils import directories
from utils.messages import error, info


def snapshot(message, quiet=False):
    """Create a snapshot of the working directory and index."""

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    status_command = ['git', 'status', '--porcelain']
    status_output = check_output(status_command).splitlines()

    if len(status_output) > 0:
        stash_command = ['git', 'stash', 'save', '-u', '--quiet']
        stash_command = stash_command if message is None else stash_command + [message]

        call(stash_command)

        # apply isn't completely quiet when the stash only contains untracked files so swallow all output
        with open(os.devnull, 'w') as devnull:
            call(['git', 'stash', 'apply', '--quiet'], stdout=devnull, stderr=STDOUT)
    else:
        info('No local changes to save. No snapshot created.', quiet)
