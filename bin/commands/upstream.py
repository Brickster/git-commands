"""Get the current upstream branch."""

from subprocess import check_output, PIPE, Popen

from commands.utils import directories
from commands.utils.messages import error

_MERGE_CONFIG = 'git config --local branch.{}.merge'
_REMOTE_CONFIG = 'git config --local branch.{}.remote'


def upstream(include_remote=False):
    """Get the upstream branch of the current branch."""

    if not directories.is_git_repository():
        error('{0!r} not a git repository'.format(os.getcwd()))

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
