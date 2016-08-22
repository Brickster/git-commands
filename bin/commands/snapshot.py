"""Create a snapshot of the changes in a dirty working directory."""

import os
import subprocess
from subprocess import STDOUT

import tuck
from utils import directories, messages


def snapshot(message=None, quiet=False, files=None):
    """Create a snapshot of the working directory and index.

    :param str or unicode message: the message to use when creating the underlying stash
    :param bool quiet: suppress all output
    :param list files: a list of pathspecs to specific files to use when creating the snapshot
    """

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))

    status_command = ['git', 'status', '--porcelain']
    status_output = subprocess.check_output(status_command).splitlines()

    if len(status_output) > 0:

        if files:
            tuck.tuck(files, message, quiet=True)
        else:
            stash_command = ['git', 'stash', 'save', '--include-untracked', '--quiet']
            stash_command = stash_command if message is None else stash_command + [message]
            subprocess.call(stash_command)

        # apply isn't completely quiet when the stash only contains untracked files so swallow all output
        with open(os.devnull, 'w') as devnull:
            subprocess.call(['git', 'stash', 'apply', '--quiet', '--index'], stdout=devnull, stderr=STDOUT)
    else:
        messages.info('No local changes to save. No snapshot created.', quiet)
