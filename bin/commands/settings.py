"""More ways to view and edit config files."""

import os
import re
import subprocess
from subprocess import PIPE, STDOUT

from utils import directories, messages


def _validate_config(config=None):
    """Validates that the directory and file specified are compatible.

    :param config: the config name
    """

    if config == 'local' and not directories.is_git_repository():
        messages.error('{0!r} is not a git repository'.format(os.getcwd()), exit_=False)
        messages.error("'local' does not apply")


def _pretty_format_configs(config_map):
    all_sections_map = {}
    result = []
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
    return result


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

    result = []
    if config is None:
        all_configs = subprocess.check_output(['git', 'config', '--list', '--null'])
    elif file_ is not None:
        all_configs = subprocess.check_output(['git', 'config', '--list', '--null', '--file', file_])
    else:
        all_configs = subprocess.check_output(['git', 'config', '--list', '--null', '--{}'.format(config)])

    if not all_configs:
        return None
    all_configs = all_configs[:-1].split('\x00')  # strip trailing null char and split on null char

    if section is not None:
        config_section = []
        for config in all_configs:
            match = re.match('^({})\.[-a-zA-Z0-9]+{}.*$'.format(section, os.linesep), config)
            if match is not None:
                config_section += [config]
        all_configs = config_section

    config_map = {}
    for config in all_configs:
        key, value = config.split(os.linesep, 1)
        config_map[key] = value

    if count:
        result = [str(len(config_map))]
    elif keys:
        result = [key[key.rfind('.') + 1:] for key in config_map.keys()]
    elif format_ == 'pretty':
        result = _pretty_format_configs(config_map)
    else:
        for key, value in config_map.iteritems():
            result += ['{}={}'.format(key, value)]
    return os.linesep.join(result)


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

    has_local = directories.is_git_repository()

    if dry_run:
        if has_local:
            _dry_destroy_section('local', section)
        _dry_destroy_section('global', section)
        _dry_destroy_section('system', section)
    else:
        with open(os.devnull, 'w') as devnull:
            if has_local:
                subprocess.call(('git', 'config', '--local', '--remove-section', section), stdout=devnull, stderr=STDOUT)
            subprocess.call(('git', 'config', '--global', '--remove-section', section), stdout=devnull, stderr=STDOUT)
            subprocess.call(('git', 'config', '--system', '--remove-section', section), stdout=devnull, stderr=STDOUT)


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

    if config is None:
        command = ('git', 'config', key)
    elif file_ is not None:
        command = ('git', 'config', '--file', file_, key)
    else:
        command = ('git', 'config', '--{}'.format(config), key)

    proc = subprocess.Popen(command, stdout=PIPE, stderr=STDOUT)
    value = proc.communicate()[0].strip()

    if not value:
        return default
    else:
        try:
            return as_type(value)
        except ValueError:
            messages.error('Cannot parse value {0!r} for key {1!r} using format {2!r}'.format(value, key, as_type.__name__))
