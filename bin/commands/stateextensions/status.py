import os
import re

from colorama import Fore

from ..utils import execute


def title():
    return 'status'


def accent(**kwargs):

    new_repository = kwargs.get('new_repository', False)
    show_color = kwargs.get('show_color', 'always')

    if new_repository:
        status_title = '{no_color}({green}master{no_color})'.format(no_color=Fore.RESET, green=Fore.GREEN)
    else:
        status_title = execute.check_output(
            ['git', '-c', 'color.status=' + show_color, 'status', '--branch', '--short']
        ).splitlines()[0]
        status_title = re.match('.*##.*? (.*)', status_title).group(1)
        status_title = '{}({})'.format(Fore.RESET, status_title)

    return status_title


def get(**kwargs):

    new_repository = kwargs.get('new_repository', False)
    show_color = kwargs.get('show_color', 'always')
    show_clean_message = kwargs.get('show_clean_message', True)

    status_command = ['git', '-c', 'color.status=' + show_color, 'status', '--short']
    if new_repository:
        no_changes_message = 'repository is empty'
    else:
        status_command += ['--untracked-files=all']
        no_changes_message = 'working directory is clean'

    status_output = execute.check_output(status_command)
    if not status_output and show_clean_message:
        status_output = 'nothing to commit, ' + no_changes_message + os.linesep

    return status_output
