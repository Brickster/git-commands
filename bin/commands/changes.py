"""List the commits between this branch and another."""

import sys
from subprocess import call, check_output

from commands.utils import directories
from commands.utils.messages import error, info


def changes(branch, details=None, color_when='auto'):
    """Print the changes between a given branch and HEAD"""

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    color_when = color_when.lower()
    if color_when == 'never' or (color_when == 'auto' and not sys.stdout.isatty()):
        color_when = 'never'
    elif color_when == 'auto' and sys.stdout.isatty():
        color_when = 'always'

    if details == 'diff':
        call(['git', 'diff', '--color={}'.format(color_when), branch, 'HEAD'])
    elif details == 'stat':
        call(['git', 'diff', '--color={}'.format(color_when), '--stat', branch, 'HEAD'])
    else:
        command = ['git', 'log', '--oneline', '{}..HEAD'.format(branch)]
        if details == 'count':
            log = check_output(command)
            log = log.splitlines()
            info(len(log))
        else:
            command += ['--color={}'.format(color_when)]
            call(command)
