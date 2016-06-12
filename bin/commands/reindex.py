"""Re-add already indexed files to the index."""

import os
from subprocess import call, check_output

from utils import directories
from utils.messages import error


def reindex():

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    indexed_files = check_output(['git', 'diff', '--name-only', '--cached']).splitlines()
    if indexed_files:
        call(['git', 'add', '--'] + indexed_files)
