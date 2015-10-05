"""More ways to view and edit config files."""

import os
import re
from subprocess import call, check_output, PIPE, Popen, STDOUT

from commands.utils import directories
from commands.utils.messages import error


def list(section, config, count, keys, format, file=None):
    """List configuration settings respecting override precedence."""

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

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
        key, value = config.split('=')
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
                result += ['\t{} = {}'.format(key, value)]
    else:
        for key, value in config_map.iteritems():
            result += ['{}={}'.format(key, value)]
    return '\n'.join(result)


def _list(**kwargs):
    list_output = list(**kwargs)
    if list_output:
        print list_output


def _dry_destroy_section(config, section):

    command = ('git', 'settings', 'list', '--format', 'compact', '--{}'.format(config), section)
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    list_output = p.communicate()[0][:-1] # just ignore stderr and removing trailing newline

    for line in list_output.splitlines():
        print 'Would be deleted from {}: {}'.format(config, line)


def destroy(section, dry_run):
    """Destroy a section from the local, global, and system config files."""

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    if dry_run:
        _dry_destroy_section('local', section)
        _dry_destroy_section('global', section)
        _dry_destroy_section('system', section)
    else:
        with open(os.devnull, 'w') as devnull:
            call(('git', 'config', '--local', '--remove-section', section), stdout=devnull, stderr=STDOUT)
            call(('git', 'config', '--global', '--remove-section', section), stdout=devnull, stderr=STDOUT)
            call(('git', 'config', '--system', '--remove-section', section), stdout=devnull, stderr=STDOUT)


def get(key, default=None, config=None, file=None, as_type=str):
    """Retrieve a configuration value.

    Arguments:
        - key: the value key
        - default: a default to return if no value is found
        - config: the config to retrieve from
        - file: a config file to retrieve from
        - as_type: a callable, built-in type, or class object used to convert the result
    """

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    if not hasattr(as_type, '__call__') and not hasattr(as_type, '__bases__'):
        raise Exception('{} is not callable'.format(as_type))

    if config is None:
        command = ('git', 'config', key)
    elif config is not None:
        command = ('git', 'config', '--file', file, key)
    else:
        command = ('git', 'config', '--{}'.format(config), key)

    p = Popen(command, stdout=PIPE, stderr=STDOUT)
    value = p.communicate()[0]

    value = default if len(value) == 0 else as_type(value.splitlines()[0])
    return value


def as_bool(value):
    """Returns whether the input is a string representation of a boolean."""

    if not isinstance(value, str):
        raise Exception('{0!r} is not a string, use bool() instead'.format(value))

    if value.lower() in ('true', 't', 'yes', 'y'):
        return True
    elif value.lower() in ('false', 'f', 'no', 'n'):
        return False
    else:
        raise Exception('{0!r} is not a boolean representation'.format(value))


def as_delimited_list(delimiter):
    """Parse a list by a specific delimiter."""

    return lambda value: value.split(delimiter) if value else []


def _get(**kwargs):
    value = get(**kwargs)
    if value is not None: print value
