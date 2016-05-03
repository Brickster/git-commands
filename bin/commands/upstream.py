"""Get the current upstream branch."""

import os
from subprocess import check_output, PIPE, Popen

from utils import directories, git
from utils.messages import error

_MERGE_CONFIG = 'git config --local branch.{}.merge'
_REMOTE_CONFIG = 'git config --local branch.{}.remote'


def upstream(branch=None, include_remote=False):
    """Get the upstream branch of the current branch.

    :param str or unicode branch: the branch whose upstream to find
    :param bool include_remote: include the remote name in the response

    :return str or unicode: the upstream branch name or an empty string
    """

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

    if not branch:
        branch = git.current_branch()
    elif not git.is_valid_reference(branch):
        error('{0!r} is not a valid branch'.format(branch))

    # get remote branch name
    proc = Popen(_MERGE_CONFIG.format(branch).split(), stdout=PIPE)
    upstream_info = proc.communicate()[0].strip()
    upstream_info = upstream_info.rsplit('/', 1)[-1]

    # optionally, get remote name
    if upstream_info and include_remote:
        remote_name = check_output(_REMOTE_CONFIG.format(branch).split()).strip()
        upstream_info = remote_name + '/' + upstream_info

    return upstream_info
