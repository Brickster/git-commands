import subprocess


def title():
    return 'reflog'


def accent():
    return None


def get(**kwargs):
    """Reflog."""

    reflog_count = kwargs['reflog_count']
    show_color = kwargs['show_color']
    return subprocess.check_output(['git', 'reflog', '-n', str(reflog_count), '--color={}'.format(show_color)])
