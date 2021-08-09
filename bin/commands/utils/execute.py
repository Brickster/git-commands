"""A collection of wrappers around subprocess."""

from __future__ import absolute_import

import os
import subprocess  # nosec


def swallow(command):
    """Execute a command, swallow all output, and return the status code.

    :param list command: command to execute
    """
    if isinstance(command, str):
        command = command.split()
    with open(os.devnull, 'w') as devnull:
        return subprocess.call(command, stdout=devnull, stderr=devnull)


def stdout(command):
    """Execute a command, swallow stderr only, and returning stdout.

    :param list command: command to execute
    """
    if isinstance(command, str):
        command = command.split()
    with open(os.devnull, 'w') as devnull:
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=devnull).communicate()[0]


def call_input(command, input_):
    if isinstance(command, str):
        command = command.split()
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    proc.communicate(input=input_)
    return proc.returncode


def execute(command):
    if isinstance(command, str):
        command = command.split()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    command_stdout, command_stderr = proc.communicate()
    return command_stdout, command_stderr, proc.returncode


def check_output(command):
    if isinstance(command, str):
        command = command.split()
    return subprocess.check_output(command)


def call(command):
    if isinstance(command, str):
        command = command.split()
    return subprocess.call(command)


def pipe(command1, command2):
    echo = subprocess.Popen(command1, stdout=subprocess.PIPE)
    subprocess.call(command2, stdin=echo.stdout)
    echo.wait()
