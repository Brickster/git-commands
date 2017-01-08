import mock
import os
import unittest
from subprocess import STDOUT

import testutils
from bin.commands import snapshot


@mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
class TestSnapshot(unittest.TestCase):

    @mock.patch('subprocess.check_output', return_value='status\noutput\n')
    @mock.patch('subprocess.call')
    def test_snapshot_noMessage(self, mock_call, mock_checkoutput, mock_isgitrepository):

        # when
        snapshot.snapshot()

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_call.assert_has_calls([
            mock.call('git stash save --include-untracked --quiet'.split()),
            mock.call('git stash apply --quiet --index'.split(), stdout=mock.ANY, stderr=STDOUT)
        ])
        self.assertEqual(mock_call.call_args[1]['stdout'].name, os.devnull)

    @mock.patch('subprocess.check_output', return_value='status\noutput\n')
    @mock.patch('subprocess.call')
    def test_snapshot_withMessage(self, mock_call, mock_checkoutput, mock_isgitrepository):

        # when
        message = 'the message'
        snapshot.snapshot(message)

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_call.assert_has_calls([
            mock.call(['git', 'stash', 'save', '--include-untracked', '--quiet', message]),
            mock.call('git stash apply --quiet --index'.split(), stdout=mock.ANY, stderr=STDOUT)
        ])
        self.assertEqual(mock_call.call_args[1]['stdout'].name, os.devnull)

    @mock.patch('subprocess.check_output', return_value='status\noutput\n')
    @mock.patch('bin.commands.tuck.tuck')
    @mock.patch('subprocess.call')
    def test_snapshot_withFiles(self, mock_call, mock_tuck, mock_checkoutput, mock_isgitrepository):

        # when
        message = None
        files = ['file1', 'file2']
        snapshot.snapshot(message, files=files)

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_tuck.assert_called_once_with(files, message, quiet=True)
        mock_call.assert_called_once_with('git stash apply --quiet --index'.split(), stdout=mock.ANY, stderr=STDOUT)
        self.assertEqual(mock_call.call_args[1]['stdout'].name, os.devnull)

    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test_snapshot_notAGitRepository(self, mock_getcwd, mock_error, mock_isgitrepository):

        mock_isgitrepository.return_value = False

        # when
        try:
            snapshot.snapshot()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_error.assert_called_once_with("'/working/dir' not a git repository")
        mock_getcwd.assert_called_once_with()

    @mock.patch('subprocess.check_output', return_value='')
    @mock.patch('bin.commands.utils.messages.info')
    def test_snapshot_notChangesToSnapshot(self, mock_info, mock_checkoutput, mock_isgitrepository):

        # when
        quiet = False
        snapshot.snapshot(quiet=quiet)

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_info.assert_called_once_with('No local changes to save. No snapshot created.', quiet)
