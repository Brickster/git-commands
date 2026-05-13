"""More ways to view and edit config files."""

import os
import re
from functools import partial

from enum import Enum

from .utils import directories, execute, git, messages


def _pretty_format_configs(config_map: dict[str, str]) -> list[str]:
    all_sections_map = _get_sections_map(config_map)
    result: list[str] = []
    for section, section_map in sorted(all_sections_map.items()):
        _append_section_header(result, section)
        _append_section_keys(result, '    {} = {}', section_map)
    return result


def _get_sections_map(config_map: dict[str, str]) -> dict[str, dict[str, str]]:
    all_sections_map: dict[str, dict[str, str]] = {}
    for key, value in config_map.items():
        match = re.match(r'^(.*)\.([-a-zA-Z0-9]+)', key)
        assert match is not None
        subkey = match.group(1)
        key = match.group(2)

        if subkey in all_sections_map:
            section_map = all_sections_map[subkey]
        else:
            section_map = {}

        section_map[key] = value
        all_sections_map[subkey] = section_map
    return all_sections_map


def _append_section_header(result: list[str], section: str) -> None:
    match = re.match(r'^([-a-zA-Z0-9]+)\.(.*)$', section)
    if match is None:
        result += [f'[{section}]']
    else:
        result += [f'[{match.group(1)} "{match.group(2)}"]']


def _append_section_keys(result: list[str], result_format: str, section_map: dict[str, str]) -> None:
    for key, value in sorted(section_map.items()):
        result += [result_format.format(key, value)]


def _count_printer(config_map: dict[str, str]) -> list[str]:
    return [str(len(config_map))]


def _keys_printer(config_map: dict[str, str]) -> list[str]:
    return [key[key.rfind('.') + 1:] for key in config_map]


def _sections_printer(config_map: dict[str, str]) -> list[str]:
    return list(set([key[0:key.rfind('.')] for key in config_map]))


def _pretty_printer(config_map: dict[str, str]) -> list[str]:
    return _pretty_format_configs(config_map)


def _compact_printer(config_map: dict[str, str]) -> list[str]:
    result: list[str] = []
    _append_section_keys(result, '{}={}', config_map)
    return result


class FormatOption(Enum):
    COMPACT = partial(_compact_printer)
    PRETTY = partial(_pretty_printer)
    COUNT = partial(_count_printer)
    KEYS = partial(_keys_printer)
    SECTIONS = partial(_sections_printer)


def list_(section: str | None = None, config: git.ConfigOption | str | None = None, format_: FormatOption = FormatOption.COMPACT) -> str | None:
    """List configuration settings respecting override precedence.

    :param section: limit to a specific section
    :param config: limit to a specific config (local|global|system)
    :param FormatOption format_: output format (compact|pretty|count|keys|sections)
    :param str or unicode file_: path to a config file to retrieve from

    :return str or unicode: configuration details
    """

    git.validate_config(config if isinstance(config, str) else None)

    # get config contents
    config = git.resolve_config_option(config)
    raw_contents = _get_config_contents(config)
    if not raw_contents:
        return None
    config_list = raw_contents[:-1].split('\x00')  # strip trailing null char and split on null char

    # optionally limit to a section of the config
    if section is not None:
        config_list = _limit_config_to_section(config_list, section)

    config_map: dict[str, str] = {}
    for config_entry in config_list:
        key, value = config_entry.split(os.linesep, 1)
        config_map[key] = value

    result = format_.value(config_map)
    return os.linesep.join(result)


def _get_config_contents(config: git.ConfigOption | str | None) -> str:
    if config is None:
        config_contents = execute.check_output(['git', 'config', '--list', '--null'])
    elif isinstance(config, git.ConfigOption):
        config_contents = execute.stdout(['git', 'config', '--list', '--null', f'--{config.name.lower()}'])
    else:
        if not os.path.exists(config):
            messages.error(f"no such file '{config}'")
        config_contents = execute.check_output(['git', 'config', '--list', '--null', '--file', config])
    return config_contents


def _limit_config_to_section(config_contents: list[str], section: str) -> list[str]:
    config_section = []
    for config in config_contents:
        match = re.match(rf'^({section})\.[-a-zA-Z0-9]+{os.linesep}.*$', config)
        if match is not None:
            config_section += [config]
    return config_section


def _dry_destroy_section(config: str, section: str) -> None:

    # get the current section
    command = ('git', 'settings', 'list', '--format', 'compact', f'--{config}', section)
    list_output = execute.stdout(command)

    # print all key/values in the section that would be removed
    for line in list_output.splitlines():
        messages.info(f'Would be deleted from {config}: {line}')


def destroy(section: str, dry_run: bool) -> None:
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
