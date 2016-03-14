"""A collection of common git actions."""

from subprocess import Popen


def is_valid_reference(reference):
    """Determines if a reference is valid.

    :param str reference: name of the reference to validate

    :return bool: whether or not the reference is valid"""

    show_ref_proc = Popen(['git', 'show-ref', '--quiet', reference])
    show_ref_proc.communicate()
    return not show_ref_proc.returncode
