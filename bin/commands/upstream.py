"""Get the current upstream branch."""

import re
from subprocess import check_output


def upstream(include_remote=False):
    """Get the upstream branch of the current branch."""

    branch_info = check_output(['git', 'status', '--porcelain', '--branch']).splitlines()[0]
    regex = '^##\s[-_a-zA-Z0-9]+\.{3}([-_a-zA-Z0-9]+/([-_a-zA-Z0-9]+))(?:\s\[.*\])?$'
    match = re.match(regex, branch_info)

    upstream_info = ''
    if match is not None:
        upstream_info = match.group(1) if include_remote else match.group(2)

    return upstream_info
