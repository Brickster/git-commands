"""Restash changes."""

import re
import sys
from subprocess import check_output, PIPE, Popen

from utils.messages import error


def restash(stash='stash@{0}'):
    """Restashes a stash reference."""

    if re.match('^stash@{.*}$', stash) is None:
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
