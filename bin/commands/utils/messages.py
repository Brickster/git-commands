import sys
from typing import IO


def _print(message: str, prefix: str | None = None, quiet: bool = False, exit_: bool = False, file_: IO[str] | None = None) -> None:
    message = prefix + ' ' + message if prefix else message
    if not quiet:
        _print_to_file(message, file_)
    if exit_:
        sys.exit(1)


def _print_to_file(message: str, file_: IO[str] | None) -> None:
    if file_:
        print(message, file=file_)
    else:
        print(message)  # defaulting file_ to sys.stdout messes with colorama


def error(message: str, prefix: str = 'error:', exit_: bool = True) -> None:
    """Print an error message and optionally exit.

    :param str or unicode message: the error message to print
    :param str or unicode prefix: the prefix to print before the message
    :param bool exit_: whether or not to exit with code 1 after printing
    """
    _print(message, prefix=prefix, exit_=exit_, file_=sys.stderr)


def warn(message: str, quiet: bool = False, ignore: bool = False) -> bool:
    """Print a simple warning message.

    Ignore repeated warnings by feeding warn() back into itself:
    warned = None
    for _ in xrange(0, 5):
        warned = warn(message, ignore=warned)

    :param str or unicode message: the warning message to print
    :param bool quiet: suppress message
    :param bool ignore: ignore this warning and print nothing
    :return bool: always returns True to indicate a warning has been issued
    """
    if not ignore:
        _print(message, prefix='warn:', quiet=quiet)
    return True


def usage(message: str) -> None:
    """Print a simple usage message.

    :param str or unicode message: the usage message to print
    """
    _print(message, prefix='usage:')


def info(message: str, quiet: bool = False) -> None:
    """Print a simple info message.

    :param str or unicode message: the message to print
    :param bool quiet: suppress message
    """
    _print(message, quiet=quiet)
