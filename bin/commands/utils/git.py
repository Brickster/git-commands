"""A collection of common git actions."""

from subprocess import check_output, PIPE, Popen, STDOUT


def is_valid_reference(reference):
    """Determines if a reference is valid.

    :param str reference: name of the reference to validate

    :return bool: whether or not the reference is valid
    """

    show_ref_proc = Popen(['git', 'show-ref', '--quiet', reference])
    show_ref_proc.communicate()
    return not show_ref_proc.returncode


def is_commit(object):
    """Determines if an object is a commit.

    :param object: a git object

    :return bool: whether or not the object is a commit object
    """

    cat_file_proc = Popen(['git', 'cat-file', '-t', object], stdout=PIPE, stderr=STDOUT)
    object_type = cat_file_proc.communicate()[0].strip()
    return not cat_file_proc.returncode and object_type == 'commit'


def current_branch():
    """Returns the current branch.

    :return str or unicode: the name of the current branch
    """

    return check_output(('git', 'rev-parse', '--abbrev-ref', 'HEAD')).strip()
