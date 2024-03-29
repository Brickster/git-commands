"""More ways to view and edit config files."""

from __future__ import absolute_import

import operator
import os
import re
from functools import partial

from enum import Enum

from .utils import directories, execute, git, messages


def _pretty_format_configs(config_map):
    all_sections_map = _get_sections_map(config_map)
    result = []
    for section, section_map in iter(sorted(all_sections_map.items(), key=operator.itemgetter(0))):
        _append_section_header(result, section)
        _append_section_keys(result, '    {} = {}', section_map)
    return result


def _get_sections_map(config_map):
    all_sections_map = {}
    for key, value in iter(config_map.items()):
        match = re.match('^(.*)\.([-a-zA-Z0-9]+)', key)
        subkey = match.group(1)
        key = match.group(2)

        if subkey in all_sections_map:
            section_map = all_sections_map[subkey]
        else:
            section_map = {}

        section_map[key] = value
        all_sections_map[subkey] = section_map
    return all_sections_map


def _append_section_header(result, section):
    match = re.match('^([-a-zA-Z0-9]+)\.(.*)$', section)
    if match is None:
        result += ['[{}]'.format(section)]
    else:
        result += ['[{} "{}"]'.format(match.group(1), match.group(2))]


def _append_section_keys(result, result_format, section_map):
    for key, value in iter(sorted(section_map.items(), key=operator.itemgetter(0))):
        result += [result_format.format(key, value)]


def _count_printer(config_map):
    return [str(len(config_map))]


def _keys_printer(config_map):
    return [key[key.rfind('.') + 1:] for key in config_map.keys()]


def _sections_printer(config_map):
    return list(set([key[0:key.rfind('.')] for key in config_map.keys()]))


def _pretty_printer(config_map):
    return _pretty_format_configs(config_map)


def _compact_printer(config_map):
    result = []
    _append_section_keys(result, '{}={}', config_map)
    return result


class FormatOption(Enum):
    COMPACT = partial(_compact_printer)
    PRETTY = partial(_pretty_printer)
    COUNT = partial(_count_printer)
    KEYS = partial(_keys_printer)
    SECTIONS = partial(_sections_printer)


def list_(section=None, config=None, format_=FormatOption.COMPACT):
    """List configuration settings respecting override precedence.

    :param section: limit to a specific section
    :param config: limit to a specific config (local|global|system)
    :param FormatOption format_: output format (compact|pretty|count|keys|sections)
    :param str or unicode file_: path to a config file

    :return str or unicode: configuration details
    """

    git.validate_config(config)

    # get config contents
    config = git.resolve_config_option(config)
    config_contents = _get_config_contents(config)
    if not config_contents:
        return None
    config_contents = config_contents[:-1].split('\x00')  # strip trailing null char and split on null char

    # optionally limit to a section of the config
    if section is not None:
        config_contents = _limit_config_to_section(config_contents, section)

    config_map = {}
    for config in config_contents:
        key, value = config.split(os.linesep, 1)
        config_map[key] = value

    result = format_.value(config_map)
    return os.linesep.join(result)


def _get_config_contents(config):
    if config is None:
        config_contents = execute.check_output(['git', 'config', '--list', '--null'])
    elif isinstance(config, git.ConfigOption):
        config_contents = execute.stdout(['git', 'config', '--list', '--null', '--{}'.format(config.name.lower())])
    else:
        if not os.path.exists(config):
            messages.error("no such file '{}'".format(config))
        config_contents = execute.check_output(['git', 'config', '--list', '--null', '--file', config])
    return config_contents


def _limit_config_to_section(config_contents, section):
    config_section = []
    for config in config_contents:
        match = re.match('^({})\.[-a-zA-Z0-9]+{}.*$'.format(section, os.linesep), config)
        if match is not None:
            config_section += [config]
    return config_section


def _dry_destroy_section(config, section):

    # get the current section
    command = ('git', 'settings', 'list', '--format', 'compact', '--{}'.format(config), section)
    list_output = execute.stdout(command)

    # print all key/values in the section that would be removed
    for line in list_output.splitlines():
        messages.info('Would be deleted from {}: {}'.format(config, line))


def destroy(section, dry_run):
    """Destroy a section from the local, global, and system config files.

    :param str or unicode section: the section to remove
    :param bool dry_run: print the sections that would be removed but don't remove them
    """

    configs = ['global', 'system']
    if directories.is_git_repository():
        configs.insert(0, 'local')

    for config in configs:
        if dry_run:
            _dry_destroy_section(config, section)
        else:
            execute.swallow(('git', 'config', '--' + config, '--remove-section', section))
