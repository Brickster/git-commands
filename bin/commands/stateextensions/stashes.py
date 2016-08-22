import subprocess


def title():
    return 'stashes'


def accent():
    return None


def get(**kwargs):
    """Run stashes"""

    show_color = kwargs['show_color']
    return subprocess.check_output(['git', 'stash', 'list', '--oneline', '--color={}'.format(show_color)])
