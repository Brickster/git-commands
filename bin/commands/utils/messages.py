from __future__ import print_function

import sys


def error(message, prefix='error:', exit=True):
    """Print an error message and optionally exit.

    :param str or unicode message: the error message to print
    :param str or unicode prefix: the prefix to print before the message
    :param bool exit: whether or not to exit with code 1 after printing
    """

    assert isinstance(message, str), "message must be a str"
    assert isinstance(exit, bool), "exit must be a bool"

    print(prefix, message, file=sys.stderr)
    if exit:
        sys.exit(1)


def warn(message):
    """Print a simple warning message."""
    info('warn: {}'.format(message), False)


def usage(message):
    """Print a simple usage message."""
    info('usage: {}'.format(message), False)


def info(message, quiet=False):
    """Print a simple info message."""

    if not quiet:
        print(message)
