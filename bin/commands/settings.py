"""More ways to view and edit config files."""

import os
import re
import subprocess
from subprocess import PIPE, STDOUT

from utils import directories, execute, messages


def _validate_config(config=None):
    """Validates that the directory and file specified are compatible.

    :param config: the config name
    """

    if config == 'local' and not directories.is_git_repository():
        messages.error('{0!r} is not a git repository'.format(os.getcwd()), exit_=False)
        messages.error("'local' does not apply")


def _pretty_format_configs(config_map):
    all_sections_map = _get_sections_map(config_map)
    result = []
    for section, section_map in all_sections_map.iteritems():
        _append_section_header(result, section)
        _append_section_keys(result, section_map)
    return result


def _get_sections_map(config_map):
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
    return all_sections_map


def _append_section_header(result, section):
    match = re.match('^([-a-zA-Z0-9]+)\.(.*)$', section)
    if match is None:
        result += ['[{}]'.format(section)]
    else:
        result += ['[{} "{}"]'.format(match.group(1), match.group(2))]


def _append_section_keys(result, section_map):
    for key, value in section_map.iteritems():
        result += ['    {} = {}'.format(key, value)]


def list_(section=None, config=None, count=False, keys=False, format_=None, file_=None):
    """List configuration settings respecting override precedence.

    :param section: limit to a specific section
    :param config: limit to a specific config (local|global|system)
    :param count: return the total configuration values count rather than the configurations themselves
    :param keys: return only the keys
    :param format_: output format (compact|pretty)
    :param str or unicode file_: path to a config file

    :return str or unicode: configuration details
    """

    _validate_config(config)

    # get config contents
    config_contents = _get_config_contents(config, file_)
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

    result = _get_list_result(count, keys, format_, config_map)
    return os.linesep.join(result)


def _get_config_contents(config, file_):
    if config is None:
        config_contents = subprocess.check_output(['git', 'config', '--list', '--null'])
    elif file_ is not None:
        if not os.path.exists(file_):
            messages.error('no such file {!r}'.format(file_))
        config_contents = subprocess.check_output(['git', 'config', '--list', '--null', '--file', file_])
    else:
        config_contents = subprocess.check_output(['git', 'config', '--list', '--null', '--{}'.format(config)])
    return config_contents


def _limit_config_to_section(config_contents, section):
    config_section = []
    for config in config_contents:
        match = re.match('^({})\.[-a-zA-Z0-9]+{}.*$'.format(section, os.linesep), config)
        if match is not None:
            config_section += [config]
    return config_section


def _get_list_result(count, keys, format_, config_map):
    if count:
        return [str(len(config_map))]
    elif keys:
        return [key[key.rfind('.') + 1:] for key in config_map.keys()]
    elif format_ == 'pretty':
        return _pretty_format_configs(config_map)

    result = []
    for key, value in config_map.iteritems():
        result += ['{}={}'.format(key, value)]
    return result


def _dry_destroy_section(config, section):

    command = ('git', 'settings', 'list', '--format', 'compact', '--{}'.format(config), section)
    proc = subprocess.Popen(command, stdout=PIPE, stderr=PIPE)
    list_output = proc.communicate()[0][:-1]  # just ignore stderr and removing trailing newline

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


def get(key, default=None, config=None, file_=None, as_type=str):
    """Retrieve a configuration value.

    :param str or unicode key: the value key
    :param str or unicode default: a default to return if no value is found
    :param str or unicode config: the config to retrieve from
    :param str or unicode file_: path to a config file to retrieve from
    :param callable as_type: a callable, built-in type, or class object used to convert the result

    :return: the configuration value
    """

    _validate_config(config)

    if not hasattr(as_type, '__call__') and not hasattr(as_type, '__bases__'):
        raise Exception('{} is not callable'.format(as_type))

    command = _get_command(key, config, file_)
    proc = subprocess.Popen(command, stdout=PIPE, stderr=STDOUT)
    value = proc.communicate()[0].strip()

    if not value:
        return default
    else:
        try:
            return as_type(value)
        except ValueError:
            messages.error('Cannot parse value {0!r} for key {1!r} using format {2!r}'.format(value, key, as_type.__name__))


def _get_command(key, config, file_):
    if config is None:
        return 'git', 'config', key
    elif file_ is not None:
        return 'git', 'config', '--file', file_, key
    return 'git', 'config', '--{}'.format(config), key
