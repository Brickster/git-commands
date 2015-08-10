"""Commits staged changes as an autosquashable fixup."""

import re
from subprocess import call, check_output

ALL = 0
UPDATE = 1


def fixup(commit, body, add_mode=None):
    """Create a fixup commit using a given commit's subject and optional body"""

    last_commit_message = check_output(['git', 'show', '--no-patch', '--format=%s', commit]).splitlines()[0]
    if re.match('^fixup!.*$', last_commit_message) is not None:
        commit_message = last_commit_message
    else:
        commit_message = 'fixup! ' + last_commit_message

    commit_command = ['git', 'commit', '--quiet', '-m', commit_message]
    if body is not None:
        commit_command += ['-m', body]

    if add_mode == ALL:
        call(['git', 'add', '--all'])
    elif add_mode == UPDATE:
        call(['git', 'add', '--update'])
    call(commit_command)
