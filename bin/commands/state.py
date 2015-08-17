"""View the state of the working tree."""

import os
import sys
from ast import literal_eval
from subprocess import call, check_output, PIPE, Popen

from . import settings
from stateextensions import branches, log, reflog, stashes, status
from utils.messages import error


class Colors:
    green = '\x1B[0;32m'
    no_color = '\x1B[0m'


def _print_section(title, text=None, format='compact', show_empty=False):
    """Print a section."""

    if not show_empty and not text:
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


def state(**kwargs):
    """Print the state of the working tree."""

    if not _is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    show_color = kwargs.get('show_color').lower()
    if show_color == 'never' or (show_color == 'auto' and not sys.stdout.isatty()):
        show_color = 'never'
        Colors.green = ''
        Colors.no_color = ''
    elif show_color == 'auto' and sys.stdout.isatty():
        show_color = 'always'
    kwargs['show_color'] = show_color

    state = ''
    format = kwargs.get('format')
    if _is_new_repository():

        status_output = status.get(new_repository=True, **kwargs)
        title = status.title(new_repository=True, **kwargs)
        state += _print_section(title, status_output, format)

    else:
        if kwargs.get('show_status'):
            status_output = status.get(**kwargs)
            state += _print_section(status.title(show_color=show_color), status_output, format, show_empty=True)

        if kwargs.get('log_count'):
            log_output = log.get(**kwargs)
            state += _print_section(log.title(), log_output, format)

        if kwargs.get('reflog_count'):
            reflog_output = reflog.get(**kwargs)
            state += _print_section(reflog.title(), reflog_output, format)

        if kwargs.get('show_branches'):
            branches_output = branches.get(**kwargs)
            state += _print_section(branches.title(), branches_output, format)

        if kwargs.get('show_stashes'):
            stashes_output = stashes.get(show_color=show_color)
            state += _print_section(stashes.title(), stashes_output, format, kwargs.get('show_empty'))

        # show any user defined sections
        extensions = settings.list(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        ).splitlines()
        extensions = list(set(extensions) - set(kwargs.get('ignore_extensions')))
        for extension in extensions or []:
            extension_command = settings.get('git-state.extensions.' + extension)
            extension_command = extension_command.split() + ['--color={}'.format(show_color)]
            extension_proc = Popen(extension_command, stdout=PIPE, stderr=PIPE)
            extension_out, extension_error = extension_proc.communicate()

            state += _print_section(
                title=extension,
                text=extension_out if not extension_proc.returncode else extension_error,
                format=format
            )


    state = state[:-1] # strip the extra trailing newline
    state_lines = len(state.splitlines())
    terminal_lines = literal_eval(check_output(['tput', 'lines']))
    if terminal_lines >= state_lines + 2: # one for the newline and one for the prompt
        if kwargs.get('clear') and sys.stdout.isatty():
            call('clear')
        print state
    else:
        echo = Popen(['echo', state], stdout=PIPE)
        call(['less', '-r'], stdin=echo.stdout)
        echo.wait()
