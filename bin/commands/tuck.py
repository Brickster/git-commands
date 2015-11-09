"""Stash specific files."""

from subprocess import call, check_output

from utils.messages import error, info


def tuck(files, message=None):
    """Stash specific files."""

    # resolve the files to be tucked
    files_to_tuck = check_output(['git', 'ls-files', '--others', '--cached', '--'] + files).splitlines()
    if not files_to_tuck:
        error("no files to tuck using: " + ' '.join(files))

    # reset the files to be tucked in the event they have changes. Like stash, we won't keep track of staged/unstaged
    # changes
    call(['git', 'reset', '--quiet', '--'] + files_to_tuck)

    # commit already staged files
    staged = check_output('git diff --name-only --cached'.split())
    if staged:
        check_output(['git', 'commit', '--message', 'TUCK: staged', '--quiet']).splitlines()

    # commit unstaged files
    ignore_files = [':!{}'.format(f) for f in files_to_tuck]
    call(['git', 'add', '--', '.'] + ignore_files)
    unstaged = check_output('git diff --name-only --cached'.split())
    if unstaged:
        call(['git', 'commit', '--message', 'TUCK: unstaged', '--quiet'])

    # stash files to be tucked
    stash_command = ['git', 'stash', 'save', '--include-untracked', '--quiet']
    if message:
        stash_command += [message]
    check_output(stash_command)

    # reset all original files
    reset_command = ['git', 'reset', '--quiet', 'HEAD^']
    if unstaged:
        call(reset_command)
    if staged:
        call(reset_command + ['--soft'])

    info('Tucked files: ' + ' '.join(files_to_tuck))
