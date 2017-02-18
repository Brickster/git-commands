"""A collection of common git actions."""

import re
import os

import subprocess
from subprocess import PIPE


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

    assert isinstance(reference, str), "'reference' must be a str. Given: " + type(reference).__name__

    show_ref_proc = subprocess.Popen(['git', 'show-ref', '--quiet', reference])
    show_ref_proc.communicate()
    return not show_ref_proc.returncode


def is_commit(object_):
    """Determines if an object is a commit.

    :param str object_: a git object

    :return bool: whether or not the object is a commit object
    """

    assert isinstance(object_, str), "'object' must be a str. Given: " + type(object_).__name__

    with open(os.devnull, 'w') as dev_null:
        cat_file_proc = subprocess.Popen(['git', 'cat-file', '-t', object_], stdout=PIPE, stderr=dev_null)
        object_type = cat_file_proc.communicate()[0].strip()
        return not cat_file_proc.returncode and object_type == 'commit'


def is_ref(object_):
    """Determines if an object is a ref.

    :param str object_: a git object

    :return bool: whether or not the object is a ref
    """

    assert isinstance(object_, str), "'object' must be a str. Given: " + type(object_).__name__

    with open(os.devnull, 'w') as dev_null:
        return not subprocess.call(('git', 'show-ref', object_), stdout=dev_null, stderr=dev_null)


def is_ref_ambiguous(ref, limit=None):
    """Determines is a ref is ambiguous.

    :param str ref: a git ref
    :param limit: ref types to limit to. May only contain: [heads, tags]

    :return bool: whether or not the ref is ambiguous

    :raise GitException: if ref is not a ref
    """

    assert isinstance(ref, str), "'ref' must be a str. Given: " + type(ref).__name__
    assert not limit or (isinstance(limit, str) and limit in ('heads', 'tags')) or \
        (isinstance(limit, (tuple, list)) and all([l in ('heads', 'tags') for l in limit])), \
        "'limit' may only contain 'heads' and/or 'tags'"

    # normalize input
    if limit and isinstance(limit, str):
        limit = [limit]

    if not is_ref(ref):
        raise GitException('{0!r} is not a ref'.format(ref))

    with open(os.devnull, 'w') as dev_null:
        if limit:
            show_ref_proc = subprocess.Popen(['git', 'show-ref'] + ['--' + l for l in limit] + [ref], stdout=PIPE, stderr=dev_null)
        else:
            show_ref_proc = subprocess.Popen(('git', 'show-ref', ref), stdout=PIPE, stderr=dev_null)
        return len(show_ref_proc.communicate()[0].splitlines()) > 1


def symbolic_full_name(ref):
    """Determines the symbolic full name for a ref.

    :param str ref: the ref

    :return str: the symbolic full name
    """

    return subprocess.check_output(('git', 'rev-parse', '--symbolic-full-name', ref)).strip()


def current_branch():
    """Returns the current branch.

    :return str or unicode: the name of the current branch
    """

    if not os.listdir('.git/refs/heads'):
        return None
    return subprocess.check_output(('git', 'rev-parse', '--abbrev-ref', 'HEAD')).strip()


def deleted_files():
    """Get the deleted files in a dirty working tree.

    :return list: a list of deleted file paths
    """

    all_files = subprocess.check_output(['git', 'status', '--short', '--porcelain'])
    return [match.group(1) for match in re.finditer('^(?:D\s|\sD)\s(.*)', all_files, re.MULTILINE)]


def is_empty_repository():
    """Determines whether a repository is empty.

    :return bool: whether or not the repository is empty
    """

    with open(os.devnull, 'w') as devnull:
        log_proc = subprocess.Popen(['git', 'log', '--oneline', '-1'], stdout=devnull, stderr=devnull)
        log_proc.wait()
        return log_proc.returncode != 0


def resolve_sha1(revision):
    """Resolve the SHA1 from a revision.

    :param str revision: revision to resolve

    :return str: SHA1
    """

    return subprocess.check_output(('git', 'rev-parse', revision)).strip()
