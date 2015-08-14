"""View the state of the working tree."""

import os
import sys
from ast import literal_eval
from subprocess import call, check_output, PIPE, Popen

from commands import settings
from stateextensions import branches, log, reflog, stashes, status
from utils.messages import error


class Colors:
    green = '\x1B[0;32m'
    no_color = '\x1B[0m'


def _print_section(title, text=None, format='compact'):
    """Print a section."""

    if not text:
        return ""

    section = '# {}{}{}'.format(Colors.green, title, Colors.no_color) + '\n'

    if format == 'pretty' and text is not None and len(text) > 0:
        # pretty print
        section += '\n'
        text = text.splitlines()
        for line in text:
            section += '    ' + line + '\n'
        section += '\n'
    elif format == 'pretty':
        # there's no text but we still want some nicer formatting
        section += '\n'
    elif format == 'compact':
        section += text
    else:
        error("unknown format '{}'".format(format))

    return section


def _is_new_repository():
    """Determines whether a repository is empty."""

    log = Popen(['git', 'log', '--oneline', '-1'], stdout=PIPE, stderr=PIPE)
    log_out, log_err = log.communicate()

    return log_err != '' and log_err.splitlines()[0] == "fatal: bad default revision 'HEAD'"


def _is_git_repository():
    """Returns whether the current working directory is a Git repository."""

    return os.path.exists('./.git')


def state(show_color, format, show_status, log_count, reflog_count, show_branches, show_stashes, show_empty, clear):
    """Print the state of the working tree."""

    if not _is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    show_only_default_branch = settings.get(
        'git-state.branches.show-only-default',
        default=True,
        as_type=settings.as_bool
    )

    show_color = show_color.lower()
    if show_color == 'never' or (show_color == 'auto' and not sys.stdout.isatty()):
        show_color = 'never'
        Colors.green = ''
        Colors.no_color = ''
    elif show_color == 'auto' and sys.stdout.isatty():
        show_color = 'always'

    state = ''
    if _is_new_repository():

        status_output = status.get(new_repository=True, show_color=show_color)
        title = status.title(new_repository=True, show_color=show_color)
        state += _print_section(title, status_output, format)

    else:
        if show_status:
            status_output = status.get(show_color=show_color)
            state += _print_section(status.title(show_color=show_color), status_output, format)

        if log_count:
            log_output = log.get(log_count=log_count, show_color=show_color)
            state += _print_section(log.title(), log_output, format)

        if reflog_count:
            reflog_output = reflog.get(reflog_count=reflog_count, show_color=show_color)
            state += _print_section(reflog.title(), reflog_output, format)

        if show_branches:
            branches_output = branches.get(show_only_default_branch=show_only_default_branch, show_color=show_color)
            state += _print_section(branches.title(), branches_output, format)

        if show_stashes:
            stashes_output = stashes.get(show_color=show_color)
            state += _print_section(stashes.title(), stashes_output, format)

    state = state[:-1] # strip the extra trailing newline
    state_lines = len(state.splitlines())
    terminal_lines = literal_eval(check_output(['tput', 'lines']))
    if terminal_lines >= state_lines + 2: # one for the newline and one for the prompt
        if clear and sys.stdout.isatty():
            call('clear')
        print state
    else:
        echo = Popen(['echo', state], stdout=PIPE)
        call(['less', '-r'], stdin=echo.stdout)
        echo.wait()
