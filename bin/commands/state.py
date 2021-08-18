"""View the state of the working tree."""

from __future__ import absolute_import

import os
import re
import shlex
import sys
from ast import literal_eval
from collections import OrderedDict

import colorama

from . import settings
from .stateextensions import status
from .utils import directories, execute, git, messages, parse_string


def _print_section(title, accent=None, text=None, format_='compact', show_empty=False, color='auto'):
    """Print a section."""

    if not show_empty and not text:
        return ""

    header_color = _resolve_header_color(color)

    if accent:
        section = '# {}{} {}{}'.format(header_color, title, accent, colorama.Fore.RESET) + os.linesep
    else:
        section = '# {}{}{}'.format(header_color, title, colorama.Fore.RESET) + os.linesep

    if format_ == 'pretty':
        section += _pretty_print_section_text(text)
    elif format_ == 'compact':
        if text is not None:
            section += text
    else:
        messages.error("unknown format '{}'".format(format_))

    return section


def _pretty_print_section_text(text):
    if text is not None and len(text) > 0:
        result = os.linesep
        text = text.splitlines()
        for line in text:
            result += '    ' + line + os.linesep
        result += os.linesep
        return result
    else:
        # there's no text but we still want some nicer formatting
        return os.linesep


def _resolve_header_color(color):
    header_color = colorama.Fore.RESET
    if color == 'auto' and sys.stdout.isatty():
        header_color = colorama.Fore.GREEN
    elif color == 'always':
        header_color = colorama.Fore.GREEN
    return header_color


def _print_sections(sections, order=[], page=False, clear=False):

    state_result = ''

    # print sections with a predefined order
    for section in order:
        if section in sections:
            state_result += sections.pop(section)

    # print any remaining sections in the order they were defined
    for section_info in sections:
        state_result += sections[section_info]

    if state_result:
        state_result = state_result[:-1]  # strip the extra trailing newline
        state_lines = len(state_result.splitlines())
        terminal_lines = literal_eval(execute.check_output(['tput', 'lines']))
        if not page or terminal_lines >= state_lines + 2:  # one for the newline and one for the prompt
            if clear and sys.stdout.isatty():
                execute.call('clear')
            messages.info(state_result)
        else:
            execute.pipe(['echo', state_result], ['less', '-r'])


def _run_extension(extension, options, show_color):
    extension_command = git.get_config_value('git-state.extensions.' + extension + '.command')
    extension_name = git.get_config_value('git-state.extensions.' + extension + '.name', default=extension)

    # merge config and command line options
    extension_options = git.get_config_value(
        'git-state.extensions.' + extension + '.options',
        default=[],
        as_type=(lambda value: [value])  # pragma: no cover since this call is mocked and the lambda never fires
    )
    extension_options += options[extension_name] if extension_name in options else []
    extension_options = [o for sub in [shlex.split(line) for line in extension_options] for o in sub]

    extension_command = shlex.split(extension_command) + extension_options
    if git.get_config_value('git-state.extensions.' + extension + '.color', default=True, as_type=parse_string.as_bool):
        extension_command += ['--color={}'.format(show_color)]

    extension_out, extension_error, extension_code = execute.execute(extension_command)
    extension_text = extension_out if not extension_code else extension_error

    return extension_name, extension_text


def _extension_exists(extension):
    return bool(int(settings.list_('git-state.extensions.' + extension, format_=settings.FormatOption.COUNT)))


def edit_extension(extension, command=None, name=None, options=None, show=None, color=True):
    extension_section = 'git-state.extensions.' + extension
    already_exists = _extension_exists(extension)
    if command:
        _update_extension_config(extension_section, 'command', command)
    if name:
        _update_extension_config(extension_section, 'name', name)
    if options:
        _update_extension_config(extension_section, 'options', options)
    if show is not None:
        _update_extension_config(extension_section, 'show', str(show))
    if color is not None:
        _update_extension_config(extension_section, 'color', str(color))
    messages.info('Extension {} {}'.format(extension, 'updated' if already_exists else 'created'))


def _update_extension_config(section, key, value):
    execute.call(['git', 'config', '--local', section + '.' + key, value])


def get_extensions():
    extensions = settings.list_(format_=settings.FormatOption.SECTIONS)
    return [match.group(1) for match in re.finditer('^git-state\\.extensions\\.([^.\n]+)$', extensions, re.MULTILINE)]


def print_extensions():
    extensions = get_extensions()
    if extensions:
        messages.info(os.linesep.join(sorted(extensions)))


def print_extension_config(extension):
    config = settings.list_(section='git-state.extensions.' + extension, format_=settings.FormatOption.PRETTY)
    if config:
        messages.info(config)


def run_extension(extension):
    if _extension_exists(extension):
        color_when = git.resolve_coloring(None)
        colorama.init(strip=(color_when == 'never'))
        extension_name, extension_text = _run_extension(extension, {}, color_when)
        format_ = git.get_config_value('git-state.format', default='compact')
        section_text = _print_section(extension_name, text=extension_text, format_=format_, show_empty=True, color=color_when)
        sections = {extension_name: section_text}
        _print_sections(sections, page=True)


def delete_extension(extension, quiet=False):
    if _extension_exists(extension):
        execute.call(['git', 'config', '--local', '--remove-section', 'git-state.extensions.{}'.format(extension)])
        messages.info('Extension {} deleted'.format(extension), quiet=quiet)


def state(**kwargs):
    """Print the state of the working tree.

    :keyword str show_color: color when (always, never, or auto)
    :keyword str format: format for output (compact or pretty)
    :keyword list ignore_extensions: extensions to hide even if the configuration is to show
    :keyword list show_extensions: extensions to show even if the configuration is to hide
    :keyword dict options: dictionary of extension to option list
    :keyword bool show_empty: show empty sections
    :keyword list order: order to print sections in
    :keyword bool clear: clear terminal before printing
    :keyword bool page: page output if too long
    """

    if not directories.is_git_repository():
        messages.error("'{}' not a git repository".format(os.getcwd()))

    show_color = git.resolve_coloring(kwargs.get('show_color').lower())
    colorama.init(strip=(show_color == 'never'))

    kwargs['show_color'] = show_color
    kwargs['show_clean_message'] = git.get_config_value(
        'git-state.status.show-clean-message',
        default=True,
        as_type=parse_string.as_bool
    )

    format_ = kwargs.get('format_')
    show_empty = kwargs.get('show_empty')
    ignore_extensions = kwargs.get('ignore_extensions')
    show_extensions = list(set(kwargs.get('show_extensions', [])))

    sections = OrderedDict()
    if git.is_empty_repository():
        extensions = ['status']
        extensions = _resolve_extensions(extensions, show_extensions, ignore_extensions)

        if 'status' in extensions:
            status_output = status.get(new_repository=True, **kwargs)
            status_title = status.title()
            status_accent = status.accent(new_repository=True, **kwargs)
            sections[status_title] = _print_section(status_title, status_accent, status_output, format_, show_empty=show_empty, color=show_color)
            extensions.remove('status')
    else:
        extensions = get_extensions() + ['status']
        extensions = _resolve_extensions(extensions, show_extensions, ignore_extensions)

        if 'status' in extensions:
            status_output = status.get(**kwargs)
            status_title = status.title()
            status_accent = status.accent(show_color=show_color)
            sections[status_title] = _print_section(status_title, status_accent, status_output, format_, show_empty=show_empty, color=show_color)
            extensions.remove('status')

        # show any user defined sections
        options = kwargs.get('options')
        for extension in extensions or []:

            # skip if we should ignore this extension
            if extension not in show_extensions and \
                    not git.get_config_value('git-state.extensions.' + extension + '.show', default=True, as_type=parse_string.as_bool):
                continue

            extension_name, extension_text = _run_extension(extension, options, show_color)

            sections[extension_name] = _print_section(
                title=extension_name,
                text=extension_text,
                format_=format_,
                show_empty=show_empty,
                color=show_color
            )

    order = kwargs.get('order', git.get_config_value('git-state.order', default=[], as_type=parse_string.as_delimited_list('|')))
    _print_sections(sections, order, kwargs.get('page', True), kwargs.get('clear'))


def _resolve_extensions(all_extensions, show_extensions, ignore_extensions):
    return list(set(show_extensions).union(set(all_extensions) - set(ignore_extensions)))
