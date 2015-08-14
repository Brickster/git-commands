from subprocess import check_output


def title():
    return 'reflog'


def get(**kwargs):
    """Reflog."""

    reflog_count = kwargs['reflog_count']
    show_color = kwargs['show_color']
    return check_output(['git', 'reflog', '-n', str(reflog_count), '--color={}'.format(show_color)])