import __main__ as main
import os
import sys


def version(version):
    '''Print a command's version'''

    assert isinstance(version, str), "str must be a str"

    command = os.path.basename(main.__file__)
    print command, version
    sys.exit()

def usage(uses, exit=True):
    """Print a usage message and optionally exit."""

    assert isinstance(exit, bool), "exit must be a bool"
    assert isinstance(uses, (tuple, list, str)), "uses must be a list, tuple, or str"
    assert len(uses) > 0, "uses cannot be empty"

    uses = uses if not isinstance(uses, str) else [uses]

    print "usage:", uses[0]
    for usage in uses[1:]:
        print "      ", usage
    if exit:
        sys.exit(2)

def error(message, exit=True):
    """Print an error message and optionally exit."""

    assert isinstance(message, str), "message must be a str"
    assert isinstance(exit, bool), "exit must be a bool"

    print "error:", message
    if exit:
        sys.exit(2)

def info(message):
    """Print a simple info message"""

    print message
