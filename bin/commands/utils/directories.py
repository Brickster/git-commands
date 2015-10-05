import os


def is_git_repository(directory='.'):
    """Returns whether the current working directory is a Git repository."""

    return os.path.exists('{}/.git'.format(directory.rstrip('/')))
