import mock
import unittest

from . import testutils
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
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call_input')
    @mock.patch('bin.commands.restash._parents', return_value=[1, 2])
    @mock.patch('bin.commands.utils.messages.info')
    def test_restash_noUntrackedFiles(self, mock_info, mock_parents, mock_callinput, mock_checkoutput, mock_isvalidstash):

        # setup
        reverse_patch_output = 'reverse patch'
        stash_sha = 'stash sha'
        mock_checkoutput.side_effect = ['stash1', reverse_patch_output, stash_sha + '\n']
        mock_callinput.return_value = 0

        # when
        restash.restash()

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'),
            mock.call('git stash show --patch --no-color stash@{0}'.split()),
            mock.call('git rev-parse stash@{0}'.split())
        ])
        mock_callinput.assert_called_once_with(['git', 'apply', '--reverse'], reverse_patch_output)
        mock_parents.assert_called_once_with('stash@{0}')
        mock_info.assert_called_once_with('Restashed stash@{{0}} ({})'.format(stash_sha), False)

    @mock.patch('bin.commands.restash._is_valid_stash', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call_input')
    @mock.patch('bin.commands.restash._parents', return_value=[1, 2, 3])
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_restash_untrackedFiles(self, mock_info, mock_call, mock_parents, mock_callinput, mock_checkoutput, mock_isvalidstash):

        # setup
        reverse_patch_output = 'reverse patch'
        stash_sha = 'stash sha'
        untracked_files = ['file1', 'file2']
        mock_checkoutput.side_effect = ['stash1', reverse_patch_output, '\n'.join(untracked_files), stash_sha + '\n']
        mock_callinput.return_value = 0

        # when
        restash.restash()

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'),
            mock.call('git stash show --patch --no-color stash@{0}'.split()),
            mock.call('git ls-tree --name-only stash@{0}^3'.split()),
            mock.call('git rev-parse stash@{0}'.split())
        ])
        mock_callinput.assert_called_once_with(['git', 'apply', '--reverse'], reverse_patch_output)
        mock_parents.assert_called_once_with('stash@{0}')
        mock_call.assert_called_once_with(['git', 'clean', '--force', '--quiet', '--'] + untracked_files)
        mock_info.assert_called_once_with('Restashed stash@{{0}} ({})'.format(stash_sha), False)

    @mock.patch('bin.commands.restash._is_valid_stash', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call_input')
    @mock.patch('bin.commands.restash._parents', return_value=[1, 2, 3])
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_restash_untrackedFiles_butNoneFound(self, mock_info, mock_call, mock_parents, mock_callinput, mock_checkoutput, mock_isvalidstash):
        """This case is possible if --include-untracked is used when not needed."""

        # setup
        reverse_patch_output = 'reverse patch'
        stash_sha = 'stash sha'
        mock_checkoutput.side_effect = ['stash1', reverse_patch_output, '', stash_sha + '\n']
        mock_callinput.return_value = 0

        # when
        restash.restash()

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'),
            mock.call('git stash show --patch --no-color stash@{0}'.split()),
            mock.call('git ls-tree --name-only stash@{0}^3'.split()),
            mock.call('git rev-parse stash@{0}'.split())
        ])
        mock_callinput.assert_called_once_with(['git', 'apply', '--reverse'], reverse_patch_output)
        mock_parents.assert_called_once_with('stash@{0}')
        mock_call.assert_not_called()
        mock_info.assert_called_once_with('Restashed stash@{{0}} ({})'.format(stash_sha), False)

    @mock.patch('bin.commands.restash._is_valid_stash', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call_input')
    @mock.patch('bin.commands.restash._parents', return_value=[1, 2, 3])
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_restash_untrackedFiles_noPatchToReverce(self, mock_info, mock_call, mock_parents, mock_callinput, mock_checkoutput, mock_isvalidstash):
        """This tests stashes consisting only of untracked files."""

        # setup
        stash_sha = 'stash sha'
        untracked_files = ['file1', 'file2']
        mock_checkoutput.side_effect = ['stash1', '', '\n'.join(untracked_files), stash_sha + '\n']

        # when
        restash.restash()

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'),
            mock.call('git stash show --patch --no-color stash@{0}'.split()),
            mock.call('git ls-tree --name-only stash@{0}^3'.split()),
            mock.call('git rev-parse stash@{0}'.split())
        ])
        mock_callinput.assert_not_called()
        mock_parents.assert_called_once_with('stash@{0}')
        mock_call.assert_called_once_with(['git', 'clean', '--force', '--quiet', '--'] + untracked_files)
        mock_info.assert_called_once_with('Restashed stash@{{0}} ({})'.format(stash_sha), False)

    @mock.patch('bin.commands.restash._is_valid_stash', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call_input')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_restash_unableToReverseApplyPath(self, mock_error, mock_callinput, mock_checkoutput, mock_isvaidstash):

        # setup
        reverse_patch_output = 'reverse patch'
        stash_sha = 'stash sha'
        mock_checkoutput.side_effect = ['stash1', reverse_patch_output, stash_sha + '\n']
        mock_callinput.return_value = 1

        # when
        try:
            restash.restash()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git stash list'),
            mock.call('git stash show --patch --no-color stash@{0}'.split())
        ])
        mock_callinput.assert_called_once_with(['git', 'apply', '--reverse'], reverse_patch_output)
        mock_error.assert_called_once_with('unable to reverse modifications', exit_=True)

    @mock.patch('bin.commands.utils.execute.check_output', return_value='')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_restash_noStashesExist(self, mock_error, mock_checkoutput):

        # when
        try:
            restash.restash()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_checkoutput.assert_called_once_with('git stash list')
        mock_error.assert_called_once_with('no stashes exist')

    @mock.patch('bin.commands.utils.execute.check_output', return_value='stash1')
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
        mock_checkoutput.assert_called_once_with('git stash list')
        mock_isvalidstash.assert_called_once_with(stash)
        mock_error.assert_called_once_with('{} is not a valid stash reference'.format(stash))

    @mock.patch('bin.commands.utils.execute.swallow')
    def test_isValidStash(self, mock_swallow):

        # setup
        mock_swallow.return_value = 0

        # when
        stash = 'stash@{2}'
        is_valid_stash = restash._is_valid_stash(stash)

        # then
        mock_swallow.assert_called_once_with(['git', 'cat-file', '-t', stash])
        self.assertEqual(is_valid_stash, True)

    @mock.patch('subprocess.Popen')
    def test_isValidStash_failsRegex(self, mock_popen):

        # when
        is_valid_stash = restash._is_valid_stash('not valid')

        # then
        self.assertEqual(is_valid_stash, False)
        mock_popen.assert_not_called()

    @mock.patch('bin.commands.utils.execute.check_output')
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
