import os

from . import messages


def is_git_repository(directory='.'):
    """Returns whether the current working directory is a Git repository."""

    return os.path.exists('{}/.git'.format(directory.rstrip('/')))


def exit_if_not_git_repository(directory=os.getcwd()):
    if not is_git_repository(directory):
        messages.error('{0!r} not a git repository'.format(directory))
