"""Get the current upstream branch."""

import os
import subprocess
from subprocess import PIPE

from utils import directories, git, messages

_MERGE_CONFIG = 'git config --local branch.{}.merge'
_REMOTE_CONFIG = 'git config --local branch.{}.remote'


def upstream(branch=None, include_remote=False):
    """Get the upstream branch of the current branch.

    :param str or unicode branch: the branch whose upstream to find
    :param bool include_remote: include the remote name in the response

    :return str or unicode: the upstream branch name or an empty string
    """

    if not directories.is_git_repository():
        messages.error('{0!r} not a git repository'.format(os.getcwd()))

    if not branch:
        branch = git.current_branch()
    elif not git.is_valid_reference(branch):
        messages.error('{0!r} is not a valid branch'.format(branch))

    # get remote branch name
    proc = subprocess.Popen(_MERGE_CONFIG.format(branch).split(), stdout=PIPE)
    upstream_info = proc.communicate()[0].strip()
    upstream_info = upstream_info.rsplit('/', 1)[-1]

    # optionally, get remote name
    if upstream_info and include_remote:
        remote_name = subprocess.check_output(_REMOTE_CONFIG.format(branch).split()).strip()
        upstream_info = remote_name + '/' + upstream_info

    return upstream_info
