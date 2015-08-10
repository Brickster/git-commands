"""More ways to view and edit config files."""

import re
from subprocess import check_output, PIPE, Popen, STDOUT


def list(section, config, count, format, file=None):
    """List configuration settings respecting override precedence."""

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
        result += [str(len(config_map))]
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
    print list(**kwargs)


def _dry_destroy_section(config, section):

    command = ('git', 'settings', 'list', '--format', 'compact', '--{}'.format(config), section)
    p = Popen(command, stdout=PIPE, stderr=PIPE)
    list_output = p.communicate()[0][:-1] # just ignore stderr and removing trailing newline

    for line in list_output.splitlines():
        print 'Would be deleted from {}: {}'.format(config, line)


def destroy(section, dry_run):
    """Destroy a section from the local, global, and system config files."""

    if dry_run:
        _dry_destroy_section('local', section)
        _dry_destroy_section('global', section)
        _dry_destroy_section('system', section)
    else:
        Popen(('git', 'config', '--local', '--remove-section', section), stdout=PIPE, stderr=STDOUT).communicate()
        Popen(('git', 'config', '--global', '--remove-section', section), stdout=PIPE, stderr=STDOUT).communicate()
        Popen(('git', 'config', '--system', '--remove-section', section), stdout=PIPE, stderr=STDOUT).communicate()


def get(key, default=None, config=None, file=None):
    """Retrieve a configuration value."""

    if config is None:
        command = ('git', 'config', key)
    elif config is not None:
        command = ('git', 'config', '--file', file, key)
    else:
        command = ('git', 'config', '--{}'.format(config), key)

    p = Popen(command, stdout=PIPE, stderr=STDOUT)
    value = p.communicate()[0]

    value = default if len(value) == 0 else value.splitlines()[0]
    return value


def _get(**kwargs):
    value = get(**kwargs)
    if value is not None: print value
