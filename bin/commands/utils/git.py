"""A collection of common git actions."""

from subprocess import Popen


def is_valid_branch(branch):
    """Determines if a branch is valid.

    :param str branch: name of the branch to validate

    :return bool: whether or not the branch is valid"""

    show_ref_proc = Popen(['git', 'show-ref',  '--verify', '--quiet', 'refs/heads/' + branch])
    show_ref_proc.communicate()
    return not show_ref_proc.returncode

