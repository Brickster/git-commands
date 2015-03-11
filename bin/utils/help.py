import __main__ as main
import os
import sys

from subprocess import call


def man(command=os.path.basename(main.__file__)):
    """Show a command's man page."""

    assert isinstance(command, str), "command must be a str"

    call(["man", command])
    sys.exit()
