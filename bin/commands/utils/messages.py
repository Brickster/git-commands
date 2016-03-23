from __future__ import print_function

import sys


def _print(message, prefix=None, quiet=False, exit=False, file=sys.stdout):

    assert isinstance(message, str), "message must be a str"
    assert not prefix or isinstance(prefix, str), "prefix must be a str"
    assert isinstance(quiet, bool), "quiet must be a bool"
    assert isinstance(exit, bool), "exit must be a bool"

    message = prefix + ' ' + message if prefix else message
    if not quiet:
        print(message, file=file)
    if exit:
        sys.exit(1)


def error(message, prefix='error:', exit=True):
    """Print an error message and optionally exit.

    :param str or unicode message: the error message to print
    :param str or unicode prefix: the prefix to print before the message
    :param bool exit: whether or not to exit with code 1 after printing
    """
    _print(message, prefix=prefix, exit=exit, file=sys.stderr)


def warn(message):
    """Print a simple warning message.

    :param str or unicode message: the warning message to print
    """
    _print(message, prefix='warn:')


def usage(message):
    """Print a simple usage message.

    :param str or unicode message: the usage message to print
    """
    _print(message, prefix='usage:')


def info(message, quiet=False):
    """Print a simple info message.

    :param str or unicode message: the message to print
    :param bool quiet: suppress message
    """
    _print(message, quiet=quiet)
