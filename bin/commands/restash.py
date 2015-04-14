import re

from subprocess import call, check_output, PIPE, Popen
from utils.messages import error


def restash(stash="stash@{0}"):
    """Restashes a stash reference."""

    if re.match("^stash@{.*}$", stash) is None:
        error('{} is not a valid stash reference'.format(stash))

    patch = Popen(['git', 'stash', 'show', '--patch', '--no-color', stash], stdout=PIPE)
    call(['git', 'apply', '--reverse'], stdin=patch.stdout)
    patch.wait()

    stash_sha = check_output(['git', 'rev-parse', stash]).splitlines()[0]
    print 'Restashed {} ({})'.format(stash, stash_sha)
