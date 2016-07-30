# if show_branches and (show_only_default_branch or not _only_default_branch()):
#     branches = check_output(['git', 'branch', '-vv', '--color={}'.format(show_color)])
#     state += _print_section('branches', branches, format)

import re
from subprocess import check_output

from .. import settings


def title():
    return 'branches'


def accent():
    return None


def _only_default_branch():
    """Determine whether the branches section only contains the default branch."""

    branches = check_output(['git', 'branch', '--no-color']).splitlines()

    if len(branches) > 1:
        return False

    default_branch = settings.get('git-state.branches.default', default='master')
    if re.match('\* {}'.format(default_branch), branches[0]):
        return True
    else:
        return False


def get(**kwargs):
    """Show branches."""

    show_color = kwargs['show_color']
    show_only_default_branch = settings.get(
        'git-state.branches.show-only-default',
        default=True,
        as_type=settings.as_bool
    )

    if show_only_default_branch or not _only_default_branch():
        return check_output(['git', 'branch', '-vv', '--color={}'.format(show_color)])
    return None
