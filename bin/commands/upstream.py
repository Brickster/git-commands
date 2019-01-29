"""Get the current upstream branch."""

import os
import subprocess
from subprocess import PIPE

from enum import Enum

from utils import directories, git, messages

_MERGE_CONFIG = 'git config --local branch.{}.merge'
_REMOTE_CONFIG = 'git config --local branch.{}.remote'
_LOCAL_REMOTE = '.'


class IncludeRemote(Enum):
    """Specify when to include remote information."""

    NEVER = 'Never include remote information'
    ALWAYS = 'Always include remote information'
    NONE_LOCAL = 'Only include remote information when not a local remote'


def upstream(branch=None, include_remote=IncludeRemote.NEVER):
    """Get the upstream branch of the current branch.

    :param str or unicode branch: the branch whose upstream to find
    :param IncludeRemote include_remote: include the remote name in the response

    :return str or unicode: the upstream branch name or an empty string
    """

    assert type(include_remote) == IncludeRemote, "'include_remote' must be a {!r}. Given {!r}".format(IncludeRemote, type(include_remote))

    if git.is_empty_repository():
        return None

    if not branch:
        branch = git.current_branch()
    elif not git.is_valid_reference(branch):
        messages.error('{0!r} is not a valid branch'.format(branch))

    # get remote branch name
    remote_branch = _get_remote_branch(branch)

    # get remote name
    remote_name = None
    if remote_branch and include_remote != IncludeRemote.NEVER:
        remote_name = subprocess.check_output(_REMOTE_CONFIG.format(branch).split()).strip()

    return _upstream_info(remote_name, remote_branch, include_remote)


def _get_remote_branch(branch):
    proc = subprocess.Popen(_MERGE_CONFIG.format(branch).split(), stdout=PIPE)
    upstream_info = proc.communicate()[0].strip()
    remote_branch = upstream_info.rsplit('/', 1)[-1]
    return remote_branch


def _upstream_info(remote_name, remote_branch, include_remote):
    if not remote_branch or not remote_name:
        return remote_branch
    elif include_remote == IncludeRemote.NONE_LOCAL and remote_name == _LOCAL_REMOTE:
        return remote_branch
    else:
        return remote_name + '/' + remote_branch
