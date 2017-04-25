import mock
import unittest
from subprocess import PIPE

import testutils
from bin.commands import tuck


class TestTuck(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._status = tuck._status
        self._resolve_files = tuck._resolve_files
        self._run = tuck._run
        self._dry_run = tuck._dry_run

    def tearDown(self):
        tuck._status = self._status
        tuck._resolve_files = self._resolve_files
        tuck._run = self._run
        tuck._dry_run = self._dry_run

    @mock.patch('subprocess.check_output')
    def test__status(self, mock_checkoutput):

        # given
        show_color = 'always'

        # when
        tuck._status(show_color)

        # then
        mock_checkoutput.assert_called_once_with(['git', '-c', 'color.ui=' + show_color, 'status', '--short'])

    @mock.patch('subprocess.check_output')
    def test__resolveFiles_withFiles_noIndexedOption_ignoreDeleted(self, mock_checkoutput):

        # given
        files = ['a', 'b', 'c', 'd', 'e', 'f']
        ignore_deleted = True
        indexed = None
        mock_checkoutput.side_effect = ['a\nb\nc\n', 'c\nd\n', 'e\nf\n']

        # when
        resolved = tuck._resolve_files(files, ignore_deleted, indexed)

        # then
        self.assertEqual(sorted(resolved), files)
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'diff', '--name-only', '--cached', '--'] + files),
            mock.call(['git', 'diff', '--name-only', '--'] + files),
            mock.call(['git', 'ls-files', '--others', '--'] + files)
        ])

    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.git.deleted_files')
    def test__resolveFiles_withFiles_noIndexedOption_doNotIgnoreDeleted_noDeletedFound(
            self,
            mock_deletedfiles,
            mock_checkoutput
    ):

        # given
        files = ['a', 'b', 'c', 'd', 'e', 'f']
        ignore_deleted = False
        indexed = None
        mock_checkoutput.side_effect = ['a\nb\nc\n', 'c\nd\n', 'e\nf\n']
        mock_deletedfiles.return_value = []

        # when
        resolved = tuck._resolve_files(files, ignore_deleted, indexed)

        # then
        self.assertEqual(sorted(resolved), files)
        mock_deletedfiles.assert_called_once()
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'diff', '--name-only', '--cached', '--'] + files),
            mock.call(['git', 'diff', '--name-only', '--'] + files),
            mock.call(['git', 'ls-files', '--others', '--'] + files)
        ])

    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.git.deleted_files')
    def test__resolveFiles_withFiles_noIndexedOption_doNotIgnoreDeleted_allDeletedFilesIncluded(
            self,
            mock_deletedfiles,
            mock_checkoutput
    ):

        # given
        files = ['a', 'b', 'c', 'd', 'e', 'f']
        ignore_deleted = False
        indexed = None
        mock_checkoutput.side_effect = ['a\nb\nc\n', 'c\nd\n', 'e\nf\n']
        mock_deletedfiles.return_value = ['b', 'd', 'e']

        # when
        resolved = tuck._resolve_files(files, ignore_deleted, indexed)

        # then
        self.assertEqual(sorted(resolved), files)
        mock_deletedfiles.assert_called_once()
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'diff', '--name-only', '--cached', '--'] + files),
            mock.call(['git', 'diff', '--name-only', '--'] + files),
            mock.call(['git', 'ls-files', '--others', '--'] + files)
        ])

    @mock.patch('bin.commands.utils.git.deleted_files')
    @mock.patch('bin.commands.utils.messages.warn')
    @mock.patch('bin.commands.utils.messages.usage')
    def test__resolveFiles_withFiles_noIndexedOption_doNotIgnoreDeleted_deletedFound(
            self,
            mock_usage,
            mock_warn,
            mock_deletedfiles
    ):

        # given
        files = ['a', 'b']
        ignore_deleted = False
        indexed = None
        mock_deletedfiles.return_value = ['b', 'y', 'z']

        # when
        try:
            tuck._resolve_files(files, ignore_deleted, indexed)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_deletedfiles.assert_called_once()
        mock_warn.assert_has_calls([
            mock.call('deleted files exist in working tree'),
            mock.call('deleted files are not considered by pathspecs and must be added explicitly or ignored')
        ])
        mock_usage.assert_has_calls([
            mock.call('git tuck -- PATHSPEC y z'),
            mock.call('git tuck --ignore-deleted -- PATHSPEC')
        ])

    @mock.patch('subprocess.check_output')
    def test__resolveFiles_noFiles_indexedOnly(self, mock_checkoutput):

        # given
        files = None
        ignore_deleted = False
        indexed = True
        expected_files = ['a', 'b']
        mock_checkoutput.return_value = '\n'.join(expected_files)

        # when
        actual_files = tuck._resolve_files(files, ignore_deleted, indexed)

        # then
        self.assertEqual(actual_files, expected_files)
        mock_checkoutput.assert_called_once_with(('git', 'diff', '--name-only', '--cached'))

    @mock.patch('subprocess.check_output')
    def test__resolveFiles_noFiles_unindexedOnly(self, mock_checkoutput):

        # given
        files = None
        ignore_deleted = False
        indexed = False
        expected_files = ['a', 'b']
        mock_checkoutput.side_effect = ['\n'.join(expected_files), '\n'.join(expected_files)]

        # when
        actual_files = tuck._resolve_files(files, ignore_deleted, indexed)

        # then
        self.assertEqual(actual_files, expected_files * 2)
        mock_checkoutput.assert_has_calls([
            mock.call(('git', 'diff', '--name-only')),
            mock.call(('git', 'ls-files', '--others'))
        ])

    def test__revolveFiles_withFiles_withIndexingOption(self):

        # given
        files = ['a']
        ignore_deleted = False
        indexed = True

        # when
        with self.assertRaises(Exception) as context:
            tuck._resolve_files(files, ignore_deleted, indexed)

        self.assertEqual(
            context.exception.message,
            'specifying files is not compatible with indexing option: index={}'.format(indexed)
        )

    @mock.patch('bin.commands.snapshot.snapshot')
    @mock.patch('subprocess.call')
    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.messages.info')
    def test__run(self, mock_info, mock_checkoutput, mock_call, mock_snapshot):

        # given
        files_to_tuck = ['a', 'b']
        ignore_files = [':!a', ':!b']
        message = 'the message'
        quiet = True
        stash_message = 'stash message'
        new_files = ''
        mock_checkoutput.side_effect = [stash_message + '\n', new_files]

        # when
        tuck._run(files_to_tuck, message, quiet)

        # then
        mock_snapshot.assert_called_once_with(None, False)
        mock_call.assert_has_calls([
            mock.call(['git', 'reset', '--quiet', '--', '.'] + ignore_files),
            mock.call(['git', 'checkout', '--quiet', '--', '.'] + ignore_files),
            mock.call(['git', 'clean', '--quiet', '-d', '--force', '--', '.'] + ignore_files),
            mock.call(['git', 'stash', 'pop', '--quiet', '--index', 'stash@{1}']),
            mock.call(['git', 'reset', '--quiet', '--'] + files_to_tuck),
            mock.call(['git', 'checkout', '--quiet', '--'] + files_to_tuck)
        ])
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'stash', 'save', '--include-untracked', message]),
            mock.call(['git', 'ls-files', '--others', '--'] + files_to_tuck)
        ])
        mock_info.assert_called_once_with(stash_message, quiet)

    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test__run_noFiles(self, mock_error):

        # when
        try:
            tuck._run(files_to_tuck=[], message='message', quiet=True)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_error.assert_called_once_with('no files to tuck')

    @mock.patch('bin.commands.snapshot.snapshot')
    @mock.patch('subprocess.call')
    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.messages.info')
    def test__run_noMessage(self, mock_info, mock_checkoutput, mock_call, mock_snapshot):

        # given
        files_to_tuck = ['a', 'b']
        ignore_files = [':!a', ':!b']
        message = None
        quiet = True
        stash_message = 'stash message'
        new_files = ['b', 'c']
        mock_checkoutput.side_effect = [stash_message + '\n', '\n'.join(new_files)]

        # when
        tuck._run(files_to_tuck, message, quiet)

        # then
        mock_snapshot.assert_called_once_with(None, False)
        mock_call.assert_has_calls([
            mock.call(['git', 'reset', '--quiet', '--', '.'] + ignore_files),
            mock.call(['git', 'checkout', '--quiet', '--', '.'] + ignore_files),
            mock.call(['git', 'clean', '--quiet', '-d', '--force', '--', '.'] + ignore_files),
            mock.call(['git', 'stash', 'pop', '--quiet', '--index', 'stash@{1}']),
            mock.call(['git', 'reset', '--quiet', '--'] + files_to_tuck),
            mock.call(['git', 'checkout', '--quiet', '--', 'a']),
            mock.call(['git', 'clean', '--quiet', '-d', '--force', '--'] + new_files)
        ])
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'stash', 'save', '--include-untracked']),
            mock.call(['git', 'ls-files', '--others', '--'] + files_to_tuck)
        ])
        mock_info.assert_called_once_with(stash_message, quiet)

    @mock.patch('bin.commands.snapshot.snapshot')
    @mock.patch('subprocess.call')
    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.messages.info')
    def test__run_withNewFiles(self, mock_info, mock_checkoutput, mock_call, mock_snapshot):

        # given
        files_to_tuck = ['a', 'b']
        ignore_files = [':!a', ':!b']
        message = None
        quiet = True
        stash_message = 'stash message'
        new_files = ''
        mock_checkoutput.side_effect = [stash_message + '\n', new_files]

        # when
        tuck._run(files_to_tuck, message, quiet)

        # then
        mock_snapshot.assert_called_once_with(None, False)
        mock_call.assert_has_calls([
            mock.call(['git', 'reset', '--quiet', '--', '.'] + ignore_files),
            mock.call(['git', 'checkout', '--quiet', '--', '.'] + ignore_files),
            mock.call(['git', 'clean', '--quiet', '-d', '--force', '--', '.'] + ignore_files),
            mock.call(['git', 'stash', 'pop', '--quiet', '--index', 'stash@{1}']),
            mock.call(['git', 'reset', '--quiet', '--'] + files_to_tuck),
            mock.call(['git', 'checkout', '--quiet', '--'] + files_to_tuck)
        ])
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'stash', 'save', '--include-untracked']),
            mock.call(['git', 'ls-files', '--others', '--'] + files_to_tuck)
        ])
        mock_info.assert_called_once_with(stash_message, quiet)

    @mock.patch('bin.commands.tuck._status')
    @mock.patch('bin.commands.utils.messages.info')
    def test__dryRun(self, mock_info, mock_status):

        # given
        files_to_tuck = ['a', 'd']
        show_color = True
        status_output = """M  a
?? b
 A c
D  d
"""
        info_message = """Would tuck:

    M  a
    D  d

Leaving working directory:

    ?? b
     A c
"""
        mock_status.return_value = status_output

        # when
        tuck._dry_run(files_to_tuck, show_color)

        # then
        mock_info.assert_called_once_with(info_message)

    @mock.patch('bin.commands.tuck._status')
    @mock.patch('bin.commands.utils.messages.info')
    def test__dryRun_withSimilarFileInSubdirectory(self, mock_info, mock_status):

        # given
        files_to_tuck = ['a']
        show_color = True
        status_output = """M  a
 M sub/a
"""
        info_message = """Would tuck:

    M  a

Leaving working directory:

     M sub/a
"""
        mock_status.return_value = status_output

        # when
        tuck._dry_run(files_to_tuck, show_color)

        # then
        mock_info.assert_called_once_with(info_message)

    @mock.patch('bin.commands.tuck._status')
    @mock.patch('bin.commands.utils.messages.info')
    def test__dryRun_withNothingRemaining(self, mock_info, mock_status):

        # given
        files_to_tuck = ['a', 'b']
        show_color = True
        status_output = """M  a
?? b
"""
        info_message = """Would tuck:

    M  a
    ?? b

Leaving working directory:

    clean
"""
        mock_status.return_value = status_output

        # when
        tuck._dry_run(files_to_tuck, show_color)

        # then
        mock_info.assert_called_once_with(info_message)

    @mock.patch('bin.commands.tuck._status')
    @mock.patch('bin.commands.utils.messages.info')
    def test__dryRun_noFilesToTuckButChangedFiles(self, mock_info, mock_status):

        # given
        show_color = True
        info_message = """Would tuck:

    nothing

Leaving working directory:

    a
    b
"""
        mock_status.return_value = "a\nb\n"

        # when
        tuck._dry_run(files_to_tuck=None, show_color=show_color)

        # then
        mock_info.assert_called_once_with(info_message)

    @mock.patch('bin.commands.tuck._status', return_value=None)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test__dryRun_workingDirectoryIsClean(self, mock_error, mock_status):

        # when
        try:
            tuck._dry_run(files_to_tuck=None, show_color=True)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_error.assert_called_once_with('no files to tuck, the working directory is clean')

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.tuck._resolve_files')
    @mock.patch('bin.commands.tuck._dry_run')
    @mock.patch('bin.commands.tuck._run')
    def test_tuck_run(self, mock_run, mock_dryrun, mock_resolvefiles, mock_isgitrepository):

        # given
        dry_run = False
        files = ['a', 'b']
        ignore_deleted = True
        indexed = True
        message = 'the message'
        quiet = True
        resolved_files = ['c', 'd']
        mock_resolvefiles.return_value = resolved_files

        # when
        tuck.tuck(files, indexed=indexed, message=message, quiet=quiet, ignore_deleted=ignore_deleted, dry_run=dry_run)

        # then
        mock_isgitrepository.assert_called_once()
        mock_resolvefiles.assert_called_once_with(files, ignore_deleted, indexed)
        mock_dryrun.assert_not_called()
        mock_run.assert_called_once_with(resolved_files, message, quiet)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.tuck._resolve_files')
    @mock.patch('bin.commands.tuck._dry_run')
    @mock.patch('bin.commands.tuck._run')
    def test_tuck_dryRun(self, mock_run, mock_dryrun, mock_resolvefiles, mock_isgitrepository):

        # given
        dry_run = True
        files = ['a', 'b']
        ignore_deleted = True
        indexed = True
        show_color = 'always'
        resolved_files = ['c', 'd']
        mock_resolvefiles.return_value = resolved_files

        # when
        tuck.tuck(files, indexed=indexed, ignore_deleted=ignore_deleted, dry_run=dry_run, show_color=show_color)

        # then
        mock_isgitrepository.assert_called_once()
        mock_resolvefiles.assert_called_once_with(files, ignore_deleted, indexed)
        mock_dryrun.assert_called_once_with(resolved_files, show_color)
        mock_run.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test_tuck_notAGitRepository(self, mock_getcwd, mock_error, mock_isgitrepository):

        # when
        try:
            tuck.tuck(['a'])
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once()
        mock_error.assert_called_once_with("'/working/dir' not a git repository")
        mock_getcwd.assert_called_once()
