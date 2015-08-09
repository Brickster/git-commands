"""Create a snapshot of the changes in a dirty working directory."""

from subprocess import call, check_output

from utils.messages import info


def snapshot(message):
    """Create a snapshot of the working directory and index."""

    status_command = ['git', 'status', '--porcelain']
    status_output = check_output(status_command).splitlines()

    if len(status_output) > 0:
        stash_command = ['git', 'stash', 'save', '-u', '--quiet']
        stash_command = stash_command if message is None else stash_command + [message]

        call(stash_command)
        call(['git', 'stash', 'apply', '--quiet'])
    else:
        info('No local changes to save. No snapshot created.')
