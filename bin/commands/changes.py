"""List the commits between this branch and another."""

from subprocess import call, check_output
from utils.messages import info


def changes(branch, details=None):
    """Print the changes between a given branch and HEAD"""

    if details == "diff":
        call(['git', 'diff', branch, 'HEAD'])
    elif details == "stat":
        call(['git', 'diff', '--stat', branch, 'HEAD'])
    else:
        command = ['git', 'log', '--oneline', '{}..HEAD'.format(branch)]
        if details == "count":
            log = check_output(command)
            log = log.splitlines()
            info(len(log))
        else:
            call(command)
