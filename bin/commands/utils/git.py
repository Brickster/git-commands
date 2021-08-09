"""A collection of common git actions."""

from __future__ import absolute_import

import os
import re
import sys

from enum import Enum

from . import directories
from . import execute
from . import messages


class RefType(Enum):
    HEADS = 1
    TAGS = 2


class GitException(Exception):  # pragma: no cover
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


def is_valid_reference(reference):
    """Determines if a reference is valid.

    :param str reference: name of the reference to validate

    :return bool: whether or not the reference is valid
    """

    return not execute.swallow(['git', 'show-ref', '--quiet', reference])


def is_commit(object_):
    """Determines if an object is a commit.

    :param str object_: a git object

    :return bool: whether or not the object is a commit object
    """

    return execute.stdout(['git', 'cat-file', '-t', object_]).strip() == 'commit'


def is_detached():
    """Returns whether HEAD is detached."""

    return not bool(symbolic_ref('HEAD'))


def symbolic_ref(object_):
    """Returns symbolic ref"""

    revolved_symbolic_ref = execute.stdout(['git', 'symbolic-ref', '--quiet', object_])
    if revolved_symbolic_ref:
        revolved_symbolic_ref = revolved_symbolic_ref.strip()
    return revolved_symbolic_ref


def is_ref(object_):
    """Determines if an object is a ref.

    :param str object_: a git object

    :return bool: whether or not the object is a ref
    """

    return not execute.swallow(['git', 'show-ref', object_])


def is_ref_ambiguous(ref, limit=None):
    """Determines is a ref is ambiguous.

    :param str ref: a git ref
    :param limit: ref types to limit to. May only contain: [heads, tags]

    :return bool: whether or not the ref is ambiguous

    :raise GitException: if ref is not a ref
    """

    # normalize input
    if limit and isinstance(limit, RefType):
        limit = [limit]

    if not is_ref(ref):
        raise GitException("'{}' is not a ref".format(ref))

    show_ref_command = ['git', 'show-ref']
    if limit:
        show_ref_command += ['--' + l.name.lower() for l in limit]
    show_ref_command += [ref]

    show_ref = execute.stdout(show_ref_command)
    return len(show_ref.splitlines()) > 1


def symbolic_full_name(ref):
    """Determines the symbolic full name for a ref.

    :param str ref: the ref

    :return str: the symbolic full name
    """

    return execute.check_output(['git', 'rev-parse', '--symbolic-full-name', ref]).strip()


def current_branch():
    """Returns the current branch. 'HEAD' is returned if detached.

    :return str or unicode: the name of the current branch
    """

    if not os.listdir('.git/refs/heads'):
        return None
    return execute.check_output('git rev-parse --abbrev-ref HEAD').strip()


def deleted_files():
    """Get the deleted files in a dirty working tree.

    :return list: a list of deleted file paths
    """

    all_files = execute.check_output('git status --short --porcelain')
    return [match.group(1) for match in re.finditer('^(?:D\\s|\\sD)\\s(.*)', all_files, re.MULTILINE)]


def is_empty_repository():
    """Determines whether a repository is empty.

    :return bool: whether or not the repository is empty
    """
    return execute.swallow(['git', 'log', '--oneline', '-1']) != 0


def resolve_sha1(revision):
    """Resolve the SHA1 from a revision.

    :param str revision: revision to resolve

    :return str: SHA1
    """

    sha1 = execute.stdout(['git', 'rev-parse', '--verify', '--quiet', revision]).strip()
    if not sha1:
        return None
    return sha1


def resolve_coloring(color):
    color_when = color.lower() if color else get_config_value('color.ui', default='auto')
    if color_when == 'auto':
        return 'always' if sys.stdout.isatty() else 'never'
    return color_when


def _get_command(key, config, file_):
    if config is None:
        return 'git', 'config', key
    elif file_ is not None:
        return 'git', 'config', '--file', file_, key
    return 'git', 'config', '--{}'.format(config), key


def validate_config(config=None):
    """Validates that the directory and file specified are compatible.

    :param config: the config name
    """

    if config == 'local' and not directories.is_git_repository():
        messages.error("'{}' is not a git repository".format(os.getcwd()), exit_=False)
        messages.error("'local' does not apply")


def get_config_value(key, default=None, config=None, file_=None, as_type=str):
    """Retrieve a configuration value.

    :param str or unicode key: the value key
    :param str or unicode default: a default to return if no value is found
    :param str or unicode config: the config to retrieve from
    :param str or unicode file_: path to a config file to retrieve from
    :param callable as_type: a callable, built-in type, or class object used to convert the result

    :return: the configuration value
    """

    validate_config(config)

    if not hasattr(as_type, '__call__') and not hasattr(as_type, '__bases__'):
        raise Exception('{} is not callable'.format(as_type))

    command = _get_command(key, config, file_)
    value = execute.stdout(command).strip()

    if not value:
        return default
    else:
        try:
            return as_type(value)
        except ValueError:
            messages.error(
                "Cannot parse value '{0}' for key '{1}' using format '{2}'".format(value, key, as_type.__name__)
            )
