"""Re-add already indexed files to the index."""

import os

from .utils import directories, execute, git, messages


def reindex():

    if not directories.is_git_repository():
        messages.error(f"'{os.getcwd()}' not a git repository")

    indexed_files = execute.check_output(['git', 'diff', '--name-only', '--cached']).splitlines()
    indexed_files = [f for f in indexed_files if f not in git.deleted_files()]
    if indexed_files:
        execute.call(['git', 'add', '--'] + indexed_files)
