from ast import literal_eval
from subprocess import call, check_output, Popen, PIPE


class Colors:
    green = '\x1B[0;32m'
    red='\x1B[0;31m'
    no_color = '\x1B[0m'


def _set_color_status(show_color):

    # make sure status will output ANSI codes
    # this must be done using config since status has no --color option
    status_color = Popen(['git', 'config', '--local', 'color.status'], stdout=PIPE, stderr=PIPE)
    color_status, status_color_err = status_color.communicate()
    color_status = color_status.rstrip()  # strip the newline
    call(['git', 'config', 'color.status', show_color])

    return color_status


def _reset_color_status(color_status):

    # reset color.status to its original setting
    if color_status == '':
        call(['git', 'config', '--unset', 'color.status'])

        # unset may leave an empty section, remove it if it is
        section_count = literal_eval(check_output(['git', 'settings', 'list', '--local', '--count', 'color']))
        if not section_count:
            call(['git', 'config', '--remove-section', 'color'])
    else:
        call(['git', 'config', 'color.status', color_status])


def title(**kwargs):

    new_repository = kwargs.get('new_repository', False)
    show_color = kwargs.get('show_color', 'always')

    if show_color == 'never':
        Colors.green = Colors.no_color
        Colors.red = Colors.no_color

    if new_repository:
        title = 'status {no_color}({green}master{no_color})'.format(no_color=Colors.no_color, green=Colors.green)
    else:
        original_color_status = _set_color_status(show_color)
        title = check_output('git status --branch --short'.split()).splitlines()[0].lstrip('# ')
        title = 'status{} ({})'.format(Colors.no_color, title)
        _reset_color_status(original_color_status)

    return title


def get(**kwargs):

    new_repository = kwargs.get('new_repository', False)
    show_color = kwargs.get('show_color', 'always')
    original_color_status = _set_color_status(show_color)

    if new_repository:
        # check if status is empty
        status_output = check_output(['git', 'status', '--short'])
        if not status_output:
            status_output = 'Empty repository'
    else:
        status_output = check_output(['git', 'status', '--short', '--untracked-files=all'])

    _reset_color_status(original_color_status)

    return status_output
