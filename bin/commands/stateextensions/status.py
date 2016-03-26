import os
import re
from subprocess import check_output

from colorama import Fore


def accent(**kwargs):

    new_repository = kwargs.get('new_repository', False)
    show_color = kwargs.get('show_color', 'always')

    if new_repository:
        status_title = '{no_color}({green}master{no_color})'.format(no_color=Fore.RESET, green=Fore.GREEN)
    else:
        status_title_pattern = re.compile('.*##.*? (.*)')
        status_title = check_output(('git', '-c', 'color.status=' + show_color, 'status', '--branch', '--short')).splitlines()[0]
        status_title = status_title_pattern.match(status_title).group(1)
        status_title = '{}({})'.format(Fore.RESET, status_title)

    return status_title


def title():
    return 'status'


def get(**kwargs):

    new_repository = kwargs.get('new_repository', False)
    show_color = kwargs.get('show_color', 'always')
    show_clean_message = kwargs.get('show_clean_message', True)

    if new_repository:
        # check if status is empty
        status_output = check_output(['git', 'status', '--short'])
        if not status_output:
            status_output = 'Empty repository'
    else:
        status_output = check_output(['git', '-c', 'color.branch=' + show_color, 'status', '--short', '--untracked-files=all'])

    if not status_output and show_clean_message:
        status_output = 'nothing to commit, working directory is clean' + os.linesep

    return status_output
