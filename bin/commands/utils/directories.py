import os

from . import messages


def is_git_repository(directory='.'):
    """Returns whether the current working directory is a Git repository."""

    return os.path.exists(f'{directory.rstrip("/")}/.git')


def exit_if_not_git_repository(directory=None):
    if directory is None:
        directory = os.getcwd()
    if not is_git_repository(directory):
        messages.error(f"'{directory}' not a git repository")
