"""Get the current upstream branch."""

import re
from subprocess import check_output, PIPE, Popen

_MERGE_CONFIG = 'git config --local branch.{}.merge'
_REMOTE_CONFIG = 'git config --local branch.{}.remote'

def upstream(include_remote=False):
    """Get the upstream branch of the current branch."""

    branch_name = check_output('git rev-parse --abbrev-ref HEAD'.split()).splitlines()[0]

    # get remote branch name
    proc = Popen(_MERGE_CONFIG.format(branch_name).split(), stdout=PIPE)
    upstream_info = proc.communicate()[0].strip()
    upstream_info = upstream_info.rsplit('/', 1)[-1]

    # optionally, get remote name
    if upstream_info and include_remote:
        remote_name = check_output(_REMOTE_CONFIG.format(branch_name).split()).strip()
        upstream_info = remote_name + '/' + upstream_info

    return upstream_info
