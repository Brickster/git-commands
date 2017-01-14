"""More ways to view and edit config files."""

import os
import re
from subprocess import call, check_output, PIPE, Popen, STDOUT

from utils import directories
from utils.messages import error

_COMMENT_PATTERN = re.compile('[#;](?P<comment>.*)')
_SECTION_PATTERN = re.compile('\[(?P<section>[a-zA-Z0-9.-]+)(?:\s+"(?P<subsection>.+)"\s*)?\](?:\s+#(?P<comment>.*))?$')
_KEY_VALUE_PATTERN = re.compile('(?P<key>[a-zA-Z][a-zA-Z0-9-]*)(?:\s?=\s?(?P<value>[^#]*)(?:\s+#(?P<comment>.*))?)?$')


class Config(object):
    def __init__(self, sections):
        self.sections = sections

    def __str__(self):
        return os.linesep.join([str(s) for s in self.sections])


class Comment(object):
    def __init__(self, comment):
        self.comment = comment

    def __str__(self):
        return '# ' + self.comment


class Section(object):
    def __init__(self, section, subsection=None, inline_comment=None, comments=None):
        self.section = section.strip()
        self.subsection = subsection.strip() if subsection else None
        self.inline_comment = inline_comment
        self.comments = comments
        self.values = []

    def __str__(self):
        result = ''
        if self.comments:
            result += os.linesep.join([str(c) for c in self.comments]) + os.linesep
        result += '[' + self.section
        if self.subsection:
            result += ' "{}"'.format(self.subsection)
        result += ']'
        if self.inline_comment:
            result += '  ' + str(self.inline_comment)

        for value in self.values:
            if isinstance(value, Comment):
                result += os.linesep + '    ' + str(value)
            else:
                result += os.linesep + str(value)

        return result


class Value(object):
    def __init__(self, key, value=True, inline_comment=None, comments=None):
        self.key = key.strip()
        self.value = value.strip() if not isinstance(value, bool) else value
        self.inline_comment = inline_comment
        self.comments = comments

    def __str__(self):
        result = ''
        if self.comments:
            result += '    ' + (os.linesep + '    ').join([str(c) for c in self.comments]) + os.linesep
        result += '    ' + self.key + ' = '
        if isinstance(self.value, bool):
            result += 'true' if self.value else 'false'
        else:
            result += self.value
        if self.inline_comment:
            result += '  ' + str(self.inline_comment)
        return result


def _parse_config(lines):
    pending_comments = []
    all_sections = []
    multi = False
    for line in lines:

        # handle multiline value
        if multi:
            line = line.rstrip()
            all_sections[-1].values[-1].value += os.linesep + line
            multi = line.endswith('\\') and not groups['comment']  # TODO: confirm subsequent lines can have comments
            continue

        line = line.strip()

        # comments
        match = _COMMENT_PATTERN.match(line)
        if match:
            pending_comments += [Comment(comment=match.groupdict()['comment'].strip())]
            continue

        # sections
        match = _SECTION_PATTERN.match(line)
        if match:
            groups = match.groupdict()
            # TODO: handle inline comments differently than attached
            all_sections += [Section(
                section=groups['section'],
                subsection=groups['subsection'],
                inline_comment=Comment(groups['comment'].strip()) if groups['comment'] else None,
                comments=pending_comments if pending_comments else None
            )]
            pending_comments = []
            continue

        # key/values
        match = _KEY_VALUE_PATTERN.match(line)
        if match:
            groups = match.groupdict()
            key_value = Value(
                key=groups['key'],
                value=groups['value'] if groups['value'] else True,
                inline_comment=Comment(groups['comment'].strip()) if groups['comment'] else None,
                comments=pending_comments if pending_comments else None
            )
            pending_comments = []
            all_sections[-1].values += [key_value]
            multi = line.endswith('\\') and not groups['comment']  # it can't be multi-line if there's an inline comment
            continue

        # skip whitespace
        if line:
            raise Exception('cannot parse line: {0!r}'.format(line))

    if pending_comments:
        all_sections += pending_comments  # TODO: may want to differentiate pending comments from previous section

    return Config(all_sections)


def _validate_config(config=None):
    """Validates that the directory and file specified are compatible.

    :param config: the config name
    """

    if config == 'local' and not directories.is_git_repository():
        error('{0!r} is not a git repository so {1!r} does not apply'.format(os.getcwd(), 'local'))


def list(section, config, count, keys, format, file=None):
    """List configuration settings respecting override precedence.

    :param section: limit to a specific section
    :param config: limit to a specific config (local|global|system)
    :param count: return the total configuration values count rather than the configurations themselves
    :param keys: return only the keys
    :param format: output format (compact|pretty)
    :param str or unicode file: path to a config file

    :return str or unicode: configuration details
    """

    _validate_config(config)

    result = []
    if config is None:
        all_configs = check_output(['git', 'config', '--list']).splitlines()
    elif file is not None:
        all_configs = check_output(['git', 'config', '--list', '--file', file]).splitlines()
    else:
        all_configs = check_output(['git', 'config', '--list', '--{}'.format(config)]).splitlines()

    if section is not None:
        config_section = []
        for config in all_configs:
            match = re.match('^({})\.[-a-zA-Z0-9]+=.*$'.format(section), config)
            if match is not None:
                config_section += [config]
        all_configs = config_section

    config_map = {}
    for config in all_configs:
        key, value = config.split('=', 1)
        config_map[key] = value

    if count:
        result = [str(len(config_map))]
    elif keys:
        result = [key[key.rfind('.') + 1 :] for key in config_map.keys()]
    elif format == 'pretty':

        all_sections_map = {}
        for key, value in config_map.iteritems():
            match = re.match('^(.*)\.([-a-zA-Z0-9]+)', key)
            subkey = match.group(1)
            key = match.group(2)

            if subkey in all_sections_map:
                section_map = all_sections_map[subkey]
            else:
                section_map = {}

            section_map[key] = value
            all_sections_map[subkey] = section_map

        for section, section_map in all_sections_map.iteritems():
            match = re.match('^([-a-zA-Z0-9]+)\.(.*)$', section)
            if match is None:
                result += ['[{}]'.format(section)]
            else:
                result += ['[{} "{}"]'.format(match.group(1), match.group(2))]
            for key, value in section_map.iteritems():
                result += ['    {} = {}'.format(key, value)]
    else:
        for key, value in config_map.iteritems():
            result += ['{}={}'.format(key, value)]
    return os.linesep.join(result)


def _list(**kwargs):
    list_output = list(**kwargs)
    if list_output:
        print list_output


def _dry_destroy_section(config, section):

    command = ('git', 'settings', 'list', '--format', 'compact', '--{}'.format(config), section)
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    list_output = proc.communicate()[0][:-1]  # just ignore stderr and removing trailing newline

    for line in list_output.splitlines():
        print 'Would be deleted from {}: {}'.format(config, line)


def destroy(section, dry_run):
    """Destroy a section from the local, global, and system config files.

    :param str or unicode section: the section to remove
    :param bool dry_run: print the sections that would be removed but don't remove them
    """

    has_local = directories.is_git_repository()

    if dry_run:
        if has_local:
            _dry_destroy_section('local', section)
        _dry_destroy_section('global', section)
        _dry_destroy_section('system', section)
    else:
        with open(os.devnull, 'w') as devnull:
            if has_local:
                call(('git', 'config', '--local', '--remove-section', section), stdout=devnull, stderr=STDOUT)
            call(('git', 'config', '--global', '--remove-section', section), stdout=devnull, stderr=STDOUT)
            call(('git', 'config', '--system', '--remove-section', section), stdout=devnull, stderr=STDOUT)


def get(key, default=None, config=None, file=None, as_type=str):
    """Retrieve a configuration value.

    :param str or unicode key: the value key
    :param str or unicode default: a default to return if no value is found
    :param str or unicode config: the config to retrieve from
    :param str or unicode file: path to a config file to retrieve from
    :param callable as_type: a callable, built-in type, or class object used to convert the result

    :return: the configuration value
    """

    _validate_config(config)

    if not hasattr(as_type, '__call__') and not hasattr(as_type, '__bases__'):
        raise Exception('{} is not callable'.format(as_type))

    if config is None:
        command = ('git', 'config', key)
    elif file is not None:
        command = ('git', 'config', '--file', file, key)
    else:
        command = ('git', 'config', '--{}'.format(config), key)

    proc = Popen(command, stdout=PIPE, stderr=STDOUT)
    value = proc.communicate()[0].strip()

    if not value:
        return default
    else:
        try:
            return as_type(value)
        except ValueError:
            error('Cannot parse value {0!r} for key {1!r} using format {2!r}'.format(value, key, as_type.__name__))
            # error('{0!r} cannot be parsed as a {1}'.format(value, as_type.__name__))


def cleanup(file_path=None):
    """Removes empty and merges duplicate sections from a config file.

    :param str or unicode file_path: path to a config file
    """

    if not os.path.isfile(file_path):
        error('no such file: {0!r}'.format(file_path), exit_=True)

    with open(file_path, 'r') as config_file:
        old_config = config_file.read().splitlines()

    config = _parse_config(old_config)

    # iterate over sections merge duplicates and remove empty ones
    visited_sections = {}
    newer_sections = []
    for section in config.sections:
        if isinstance(section, Section) and section.values:
            name = section.section + (section.subsection if section.subsection else '')
            if name in visited_sections:
                # TODO: merge section level comments somehow
                visited_sections[name].values += section.values
            else:
                visited_sections[name] = section
                newer_sections += [section]
        elif not isinstance(section, Section):
            newer_sections += [section]
    config.sections = newer_sections

    with open(file_path, 'w') as config_file:
        config_file.write(str(config))
        config_file.write(os.linesep)


def _get(**kwargs):
    value = get(**kwargs)
    if value is not None:
        print value
