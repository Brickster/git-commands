from subprocess import check_output


def title():
    return 'stashes'


def get(**kwargs):
    """Run stashes"""

    show_color = kwargs['show_color']
    return check_output(['git', 'stash', 'list', '--oneline', '--color={}'.format(show_color)])