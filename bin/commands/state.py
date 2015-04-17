import re

from ast import literal_eval
from subprocess import call, check_output, PIPE, Popen
from utils.messages import error

class colors:
    green = "\x1B[0;32m"
    no_color = "\x1B[0m"


def _print_section(title, text=None, format="compact"):
    """Print a section."""

    section = "# {}{}{}".format(colors.green, title, colors.no_color) + '\n'

    if format == "pretty" and text is not None and len(text) > 0:
        # pretty print
        section += '\n'
        text = text.splitlines()
        for line in text:
            section += "    " + line + '\n'
        section += '\n'
    elif format == 'pretty':
        # there's no text but we still want some nicer formatting
        section += '\n'
    elif format == 'compact':
        section += text
    else:
        error("unknown format '{}'".format(format))

    return section


def _only_default_branch():
    """Determine whether the branches section only contains the default branch."""

    branches = check_output(['git', 'branch', '--no-color']).splitlines()

    if len(branches) > 1:
        return False

    default_branch = check_output(['git', 'settings', 'get', '-d', 'master', 'git-state.branches.default']).splitlines()[0]
    if re.match('\* {}'.format(default_branch), branches[0]) is not None:
        return True
    else:
        return False


def _is_new_repository():
    """Determines whether a repository is empty."""

    log = Popen(['git', 'log', '--oneline', '-1'], stdout=PIPE, stderr=PIPE)
    log_out, log_err = log.communicate()

    return log_err != '' and log_err.splitlines()[0] == "fatal: bad default revision 'HEAD'"


def state(show_color, format, show_status, log_count, reflog_count, show_branches, show_stashes, show_empty):

    show_only_default_branch = literal_eval(check_output(['git', 'settings', 'get', '-d', 'True', 'git-state.branches.show-only-default']))

    if show_color:
        color = "always"
    else:
        color = "never"
        colors.green = ""
        colors.no_color = ""

    state = ''
    if _is_new_repository():

        # make sure status will output ANSI codes
        # this must be done using config since status has no --color option
        status_color = Popen(['git', 'config', '--local', 'color.status'], stdout=PIPE, stderr=PIPE)
        status_color_out, status_color_err = status_color.communicate()
        status_color_out = status_color_out.rstrip()  # strip the newline
        call(['git', 'config', 'color.status', color])

        # check if status is empty
        status = check_output(['git', 'status', '--short'])
        if status == "":
            status = "Initial commit"

        title = 'status {}({}master{})'.format(colors.no_color, colors.green, colors.no_color)
        state += _print_section(title, status, format)

        # reset color.status to its original setting
        if status_color_out == '':
            call(['git', 'config', '--unset', 'color.status'])

            # unset may leave an empty section, remove it if it is
            section_count = literal_eval(check_output(['git', 'settings', 'list', '--local', '--count', color]))
            if section_count == 0:
                call(['git', 'config', '--remove-section', 'color'])
        else:
            call(['git', 'config', 'color.status', status_color_out])

    else:
        if show_status:

            # make sure status will output ANSI codes
            # this must be done using config since status has no --color option
            status_color = Popen(['git', 'config', '--local', 'color.status'], stdout=PIPE, stderr=PIPE)
            status_color_out, status_color_err = status_color.communicate()
            status_color_out = status_color_out.rstrip()  # strip the newline
            call(['git', 'config', 'color.status', color])

            status = check_output(['git', 'status', '--short', '--untracked-files=all', '--branch']).splitlines()
            status_title = 'status {}({})'.format(colors.no_color ,status.pop(0).lstrip('# '))
            status = '\n'.join(status)
            state += _print_section(status_title, status, format)

            # reset color.status to its original setting
            if status_color_out == '':
                call(['git', 'config', '--unset', 'color.status'])

                # unset may leave an empty section, remove it if it is
                section_count = literal_eval(check_output(['git', 'settings', 'list', '--local', '--count', color]))
                if section_count == 0:
                    call(['git', 'config', '--remove-section', 'color'])
            else:
                call(['git', 'config', 'color.status', status_color_out])

        if log_count != 0:
            log = check_output(['git', 'log', '-n', str(log_count), '--oneline', '--color={}'.format(color)])
            state += _print_section("log", log, format)

        if reflog_count != 0:
            reflog = check_output(['git', 'reflog', '-n', str(reflog_count), '--color={}'.format(color)])
            state += _print_section('reflog', reflog, format)

        if show_branches and (show_only_default_branch or not _only_default_branch()):
            branches = check_output(['git', 'branch', '-vv', '--color={}'.format(color)])
            state += _print_section('branches', branches, format)

        stashes = stashes = check_output(['git', 'stash', 'list', '--oneline', '--color={}'.format(color)])
        if show_stashes and (show_empty or len(stashes) > 0):
            state += _print_section('stashes', stashes, format)

    state = state[:-1] # strip the extra trailing newline
    state_lines = len(state.splitlines())
    terminal_lines = literal_eval(check_output(['tput', 'lines']))
    if terminal_lines >= state_lines + 2: # one for the newline and one for the prompt
        print state
    else:
        echo = Popen(['echo', state], stdout=PIPE)
        call(['less', '-r'], stdin=echo.stdout)
        echo.wait()

