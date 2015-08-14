import re
from ast import literal_eval
from subprocess import call, check_output, Popen, PIPE

from .. import upstream


class Colors:
    green = '\x1B[0;32m'
    red='\x1B[0;31m'
    no_color = '\x1B[0m'


def title(show_color):
    if show_color == 'never':
        Colors.green = Colors.no_color
        Colors.red = Colors.no_color

    branches = check_output(('git', 'branch')).splitlines()
    branch = [m.group(1) for branch in branches for m in [re.match(r'\* (.*)', branch)] if m][0]
    upstream_output = upstream.upstream(True)

    if upstream_output:
        return 'status{no_color} ({green}{branch}{no_color}...{red}{remote}{no_color})'.format(
            no_color=Colors.no_color,
            green=Colors.green,
            red=Colors.red,
            branch=branch,
            remote=upstream_output
        )
    else:
        return 'status{no_color} ({green}{branch}{no_color})'.format(
            no_color=Colors.no_color,
            green=Colors.green,
            branch=branch
        )


def get(**kwargs):
    show_color = kwargs['show_color']

    # make sure status will output ANSI codes
    # this must be done using config since status has no --color option
    status_color = Popen(['git', 'config', '--local', 'color.status'], stdout=PIPE, stderr=PIPE)
    status_color_out, status_color_err = status_color.communicate()
    status_color_out = status_color_out.rstrip()  # strip the newline
    call(['git', 'config', 'color.status', show_color])

    status = check_output(['git', 'status', '--short', '--untracked-files=all'])

    # reset color.status to its original setting
    if status_color_out == '':
        call(['git', 'config', '--unset', 'color.status'])

        # unset may leave an empty section, remove it if it is
        section_count = literal_eval(check_output(['git', 'settings', 'list', '--local', '--count', 'color']))
        if not section_count:
            call(['git', 'config', '--remove-section', 'color'])
    else:
        call(['git', 'config', 'color.status', status_color_out])

    return status