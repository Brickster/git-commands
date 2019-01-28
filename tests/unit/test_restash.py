import mock
import os
import unittest
from subprocess import PIPE

import testutils
from bin.commands import restash


class TestRestash(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._is_valid_stash = restash._is_valid_stash
        self._parents = restash._parents

    def tearDown(self):
        restash._is_valid_stash = self._is_valid_stash
        restash._parents = self._parents

    @mock.patch('bin.commands.restash._is_valid_stash', return_value=True)
    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.Popen')
    @mock.patch('bin.commands.restash._parents', return_value=[1, 2])
    @mock.patch('bin.commands.utils.messages.info')
    def test_restash_noUntrackedFiles(self, mock_info, mock_parents, mock_popen, mock_checkoutput, mock_isvalidstash):

        # setup
        reverse_patch_output = 'reverse patch'
        stash_sha = 'stash sha'
        mock_checkoutput.side_effect = ['stash1', reverse_patch_output, stash_sha + '\n']
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # when
        restash.restash()

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'.split()),
            mock.call('git stash show --patch --no-color stash@{0}'.split()),
            mock.call('git rev-parse stash@{0}'.split())
        ])
        mock_popen.assert_called_once_with(['git', 'apply', '--reverse'], stdin=PIPE)
        mock_process.communicate.assert_called_once_with(input=reverse_patch_output)
        mock_parents.assert_called_once_with('stash@{0}')
        mock_info.assert_called_once_with('Restashed stash@{{0}} ({})'.format(stash_sha), False)

    @mock.patch('bin.commands.restash._is_valid_stash', return_value=True)
    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.Popen')
    @mock.patch('bin.commands.restash._parents', return_value=[1, 2, 3])
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_restash_untrackedFiles(self, mock_info, mock_call, mock_parents, mock_popen, mock_checkoutput, mock_isvalidstash):

        # setup
        reverse_patch_output = 'reverse patch'
        stash_sha = 'stash sha'
        untracked_files = ['file1', 'file2']
        mock_checkoutput.side_effect = ['stash1', reverse_patch_output, '\n'.join(untracked_files), stash_sha + '\n']
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # when
        restash.restash()

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'.split()),
            mock.call('git stash show --patch --no-color stash@{0}'.split()),
            mock.call('git ls-tree --name-only stash@{0}^3'.split()),
            mock.call('git rev-parse stash@{0}'.split())
        ])
        mock_popen.assert_called_once_with(['git', 'apply', '--reverse'], stdin=PIPE)
        mock_process.communicate.assert_called_once_with(input=reverse_patch_output)
        mock_parents.assert_called_once_with('stash@{0}')
        mock_call.assert_called_once_with(['git', 'clean', '--force', '--quiet', '--'] + untracked_files)
        mock_info.assert_called_once_with('Restashed stash@{{0}} ({})'.format(stash_sha), False)

    @mock.patch('bin.commands.restash._is_valid_stash', return_value=True)
    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.Popen')
    @mock.patch('bin.commands.restash._parents', return_value=[1, 2, 3])
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_restash_untrackedFiles_butNoneFound(self, mock_info, mock_call, mock_parents, mock_popen, mock_checkoutput, mock_isvalidstash):
        """This case is possible if --include-untracked is used when not needed."""

        # setup
        reverse_patch_output = 'reverse patch'
        stash_sha = 'stash sha'
        mock_checkoutput.side_effect = ['stash1', reverse_patch_output, '', stash_sha + '\n']
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # when
        restash.restash()

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'.split()),
            mock.call('git stash show --patch --no-color stash@{0}'.split()),
            mock.call('git ls-tree --name-only stash@{0}^3'.split()),
            mock.call('git rev-parse stash@{0}'.split())
        ])
        mock_popen.assert_called_once_with(['git', 'apply', '--reverse'], stdin=PIPE)
        mock_process.communicate.assert_called_once_with(input=reverse_patch_output)
        mock_parents.assert_called_once_with('stash@{0}')
        mock_call.assert_not_called()
        mock_info.assert_called_once_with('Restashed stash@{{0}} ({})'.format(stash_sha), False)

    @mock.patch('bin.commands.restash._is_valid_stash', return_value=True)
    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.Popen')
    @mock.patch('bin.commands.restash._parents', return_value=[1, 2, 3])
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_restash_untrackedFiles_noPatchToReverce(self, mock_info, mock_call, mock_parents, mock_popen, mock_checkoutput, mock_isvalidstash):
        """This tests stashes consisting only of untracked files."""

        # setup
        stash_sha = 'stash sha'
        untracked_files = ['file1', 'file2']
        mock_checkoutput.side_effect = ['stash1', '', '\n'.join(untracked_files), stash_sha + '\n']
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # when
        restash.restash()

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'.split()),
            mock.call('git stash show --patch --no-color stash@{0}'.split()),
            mock.call('git ls-tree --name-only stash@{0}^3'.split()),
            mock.call('git rev-parse stash@{0}'.split())
        ])
        mock_popen.assert_not_called()
        mock_parents.assert_called_once_with('stash@{0}')
        mock_call.assert_called_once_with(['git', 'clean', '--force', '--quiet', '--'] + untracked_files)
        mock_info.assert_called_once_with('Restashed stash@{{0}} ({})'.format(stash_sha), False)

    @mock.patch('bin.commands.restash._is_valid_stash', return_value=True)
    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.Popen')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_restash_unableToReverseApplyPath(self, mock_error, mock_popen, mock_checkoutput, mock_isvaidstash):

        # setup
        reverse_patch_output = 'reverse patch'
        stash_sha = 'stash sha'
        mock_checkoutput.side_effect = ['stash1', reverse_patch_output, stash_sha + '\n']
        mock_process = mock.Mock()
        mock_process.returncode = 1
        mock_popen.return_value = mock_process

        # when
        try:
            restash.restash()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'.split()),
            mock.call('git stash show --patch --no-color stash@{0}'.split())
        ])
        mock_popen.assert_called_once_with(['git', 'apply', '--reverse'], stdin=PIPE)
        mock_process.communicate.assert_called_once_with(input=reverse_patch_output)
        mock_error.assert_called_once_with('unable to reverse modifications', exit_=True)

    @mock.patch('subprocess.check_output', return_value='')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_restash_noStashesExist(self, mock_error, mock_checkoutput):

        # when
        try:
            restash.restash()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_checkoutput.assert_called_once_with('git stash list'.split())
        mock_error.assert_called_once_with('no stashes exist')

    @mock.patch('subprocess.check_output', return_value='stash1')
    @mock.patch('bin.commands.restash._is_valid_stash', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_restash_invalidStash(self, mock_error, mock_isvalidstash, mock_checkoutput):

        # when
        stash = 'stash@{10}'
        try:
            restash.restash(stash)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_checkoutput.assert_called_once_with('git stash list'.split())
        mock_isvalidstash.assert_called_once_with(stash)
        mock_error.assert_called_once_with('{} is not a valid stash reference'.format(stash))

    @mock.patch('subprocess.Popen')
    def test_isValidStash(self, mock_popen):

        # setup
        mock_wait = mock.Mock()
        mock_process = mock.Mock()
        mock_process.wait = mock_wait
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # when
        stash = 'stash@{2}'
        is_valid_stash = restash._is_valid_stash(stash)

        # then
        self.assertEqual(is_valid_stash, True)
        mock_popen.assert_called_once_with(('git', 'cat-file', '-t', stash), stdout=mock.ANY, stderr=mock.ANY)
        self.assertEqual(mock_popen.call_args[1]['stdout'].name, os.devnull)
        self.assertEqual(mock_popen.call_args[1]['stderr'].name, os.devnull)
        mock_wait.assert_called_once_with()

    @mock.patch('subprocess.Popen')
    def test_isValidStash_failsRegex(self, mock_popen):

        # when
        is_valid_stash = restash._is_valid_stash('not valid')

        # then
        self.assertEqual(is_valid_stash, False)
        mock_popen.assert_not_called()

    @mock.patch('subprocess.check_output')
    def test_parents(self, mock_checkoutput):

        # setup
        expected_parents = ['p1', 'p2', 'p3']
        mock_checkoutput.return_value = ' '.join(['p0'] + expected_parents)

        # when
        commit = 'sha123'
        actual_parents = restash._parents(commit)

        # then
        self.assertEqual(actual_parents, expected_parents)
        mock_checkoutput.assert_called_once_with(['git', 'rev-list', '--parents', '-1', commit])
