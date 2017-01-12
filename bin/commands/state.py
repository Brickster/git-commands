"""View the state of the working tree."""

import os
import shlex
import subprocess
import sys
from ast import literal_eval
from collections import OrderedDict
from subprocess import PIPE

import colorama

from . import settings
from stateextensions import status
from utils import directories, git, messages


def _print_section(title, accent=None, text=None, format_='compact', show_empty=False):
    """Print a section."""

    if not show_empty and not text:
        return ""

    if accent:
        section = '# {}{} {}{}'.format(colorama.Fore.GREEN, title, accent, colorama.Fore.RESET) + os.linesep
    else:
        section = '# {}{}{}'.format(colorama.Fore.GREEN, title, colorama.Fore.RESET) + os.linesep

    if format_ == 'pretty' and text is not None and len(text) > 0:
        # pretty print
        section += os.linesep
        text = text.splitlines()
        for line in text:
            section += '    ' + line + os.linesep
        section += os.linesep
    elif format_ == 'pretty':
        # there's no text but we still want some nicer formatting
        section += os.linesep
    elif format_ == 'compact':
        section += text
    else:
        messages.error("unknown format '{}'".format(format_))

    return section


def state(**kwargs):
    """Print the state of the working tree."""

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))

    show_color = kwargs.get('show_color').lower()
    if show_color == 'never' or (show_color == 'auto' and not sys.stdout.isatty()):
        show_color = 'never'
        colorama.init(strip=True)
    else:
        show_color = 'always'
        colorama.init()

    kwargs['show_color'] = show_color
    kwargs['show_clean_message'] = settings.get(
        'git-state.status.show-clean-message',
        default=True,
        as_type=settings.as_bool
    )

    format_ = kwargs.get('format')
    if git.is_empty_repository():
        status_output = status.get(new_repository=True, **kwargs)
        status_title = status.title()
        status_accent = status.accent(new_repository=True, **kwargs)
        sections = {status_title: _print_section(status_title, status_accent, status_output, format_)}
    else:
        sections = OrderedDict()
        if kwargs.get('show_status'):
            status_output = status.get(**kwargs)
            status_title = status.title()
            status_accent = status.accent(show_color=show_color)
            sections[status_title] = _print_section(status_title, status_accent, status_output, format_, show_empty=True)

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
        show_extensions = kwargs.get('show_extensions', [])
        options = kwargs.get('options')
        for extension in extensions or []:

            # skip if we should ignore this extension
            if extension not in show_extensions and not settings.get('git-state.extensions.' + extension + '.show', default=True, as_type=settings.as_bool):
                continue

            extension_command = settings.get('git-state.extensions.' + extension)
            extension_name = settings.get('git-state.extensions.' + extension + '.name', default=extension)

            # merge config and command line options
            extension_options = settings.get(
                'git-state.extensions.' + extension + '.options',
                default=[],
                as_type=(lambda value: [value])  # pragma: no cover since this call is mocked and the lambda never fires
            )
            extension_options += options[extension_name] if extension_name in options else []
            extension_options = [o for sub in [shlex.split(line) for line in extension_options] for o in sub]

            extension_command = shlex.split(extension_command) + extension_options
            if settings.get('git-state.extensions.' + extension + '.color', default=True, as_type=settings.as_bool):
                extension_command += ['--color={}'.format(show_color)]

            extension_proc = subprocess.Popen(extension_command, stdout=PIPE, stderr=PIPE)
            extension_out, extension_error = extension_proc.communicate()

            sections[extension_name] = _print_section(
                title=extension_name,
                text=extension_out if not extension_proc.returncode else extension_error,
                format_=format_,
                show_empty=kwargs.get('show_empty')
            )

    state_result = ''

    # print sections with a predefined order
    order = kwargs.get('order', settings.get('git-state.order', default=[], as_type=settings.as_delimited_list('|')))
    for section in order:
        if section in sections:
            state_result += sections.pop(section)

    # print any remaining sections in the order they were defined
    for section_info in sections:
        state_result += sections[section_info]

    state_result = state_result[:-1] # strip the extra trailing newline
    state_lines = len(state_result.splitlines())
    terminal_lines = literal_eval(subprocess.check_output(['tput', 'lines']))
    if terminal_lines >= state_lines + 2: # one for the newline and one for the prompt
        if kwargs.get('clear') and sys.stdout.isatty():
            subprocess.call('clear')
        messages.info(state_result)  # TODO: breaks --no-color
    else:
        echo = subprocess.Popen(['echo', state_result], stdout=PIPE)
        subprocess.call(['less', '-r'], stdin=echo.stdout)
        echo.wait()
