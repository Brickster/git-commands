from subprocess import check_output


def title():
    return 'log'


def accent():
    return None


def get(**kwargs):
    """Log."""

    log_count = kwargs['log_count']
    show_color = kwargs['show_color']
    return check_output(['git', 'log', '-n', str(log_count), '--oneline', '--color={}'.format(show_color)])
