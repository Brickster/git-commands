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
        return subprocess.call(command, stdout=devnull, stderr=devnull)  # nosec


def stdout(command):
    """Execute a command, swallow stderr only, and returning stdout.

    :param list command: command to execute
    """
    if isinstance(command, str):
        command = command.split()
    with open(os.devnull, 'w') as devnull:
        return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=devnull).communicate()[0].decode('UTF-8')  # nosec


def call_input(command, input_):
    if isinstance(command, str):
        command = command.split()
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)  # nosec
    proc.communicate(input=input_.encode('UTF-8'))
    return proc.returncode


def execute(command):
    if isinstance(command, str):
        command = command.split()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # nosec
    command_stdout, command_stderr = proc.communicate()
    return command_stdout.decode('UTF-8'), command_stderr.decode('UTF-8'), proc.returncode


def check_output(command):
    if isinstance(command, str):
        command = command.split()
    return subprocess.check_output(command).decode('UTF-8')  # nosec


def call(command):
    if isinstance(command, str):
        command = command.split()
    return subprocess.call(command)  # nosec


def pipe(command1, command2):
    if isinstance(command1, str):
        command1 = command1.split()
    if isinstance(command2, str):
        command2 = command2.split()
    command1_proc = subprocess.Popen(command1, stdout=subprocess.PIPE)  # nosec
    subprocess.call(command2, stdin=command1_proc.stdout)  # nosec
    command1_proc.wait()
