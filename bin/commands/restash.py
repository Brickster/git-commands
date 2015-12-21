"""Restash changes."""

import os
import re
import sys
from subprocess import check_output, PIPE, Popen

from utils import directories
from utils.messages import error


def _is_valid_stash(stash):
    """Determines if a stash reference is valid."""

    if re.match('^stash@{.*}$', stash) is None:
        return False

    with open(os.devnull, 'w') as devnull:
        proc = Popen(('git', 'cat-file', '-t', stash), stdout=devnull, stderr=devnull)
        proc.wait()
        return proc.returncode == 0


def restash(stash='stash@{0}'):
    """Restash a stash reference."""

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    if not _is_valid_stash(stash):
        error('{} is not a valid stash reference'.format(stash))

    patch = Popen(['git', 'stash', 'show', '--patch', '--no-color', stash], stdout=PIPE)
    restash_proc = Popen(['git', 'apply', '--reverse'], stdin=patch.stdout)
    patch.communicate()
    restash_proc.communicate()

    if not restash_proc.returncode:
        stash_sha = check_output(['git', 'rev-parse', stash]).splitlines()[0]
        print 'Restashed {} ({})'.format(stash, stash_sha)
    else:
        sys.exit(1)
