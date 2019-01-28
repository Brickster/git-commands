"""A collection of wrappers around subprocess."""

import os
import subprocess


def swallow(command):
    """Execute a command and swallow all output.

    :param list command: command to execute
    """
    with open(os.devnull, 'w') as devnull:
        subprocess.call(command, stdout=devnull, stderr=subprocess.STDOUT)
