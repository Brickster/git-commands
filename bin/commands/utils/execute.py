"""A collection of wrappers around subprocess."""

import os
import subprocess


def swallow(command):
    """Execute a command and swallow all output.

    :param list command: command to execute
    """
    with open(os.devnull, 'w') as devnull:
        subprocess.call(command, stdout=devnull, stderr=subprocess.STDOUT)


def stdout(command):
    """Execute a command swallowing stderr and return output.

    :param list command: command to execute
    """
    with open(os.devnull, 'w') as devnull:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=devnull)
        command_stdout = proc.communicate()[0]
    return command_stdout
