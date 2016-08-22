import re
import subprocess

from .. import settings


def title():
    return 'branches'


def accent():
    return None


def _only_default_branch():
    """Determine whether the branches section only contains the default branch."""

    branches = subprocess.check_output(['git', 'branch', '--no-color']).splitlines()

    if len(branches) > 1:
        return False

    default_branch = settings.get('git-state.branches.default', default='master')
    return bool(re.match('\* {}'.format(default_branch), branches[0]))


def get(**kwargs):
    """Show branches."""

    show_color = kwargs['show_color']
    show_only_default_branch = settings.get(
        'git-state.branches.show-only-default',
        default=True,
        as_type=settings.as_bool
    )

    if show_only_default_branch or not _only_default_branch():
        return subprocess.check_output(['git', 'branch', '-vv', '--color={}'.format(show_color)])
    return None
