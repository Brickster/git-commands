import mock
import unittest

from bin.commands import snapshot


class TestSnapshotSnapshot(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._stash_buffer = snapshot._stash_buffer

    def tearDown(self):
        snapshot._stash_buffer = self._stash_buffer

    @mock.patch('subprocess.check_output', return_value='status\noutput\n')
    @mock.patch('bin.commands.snapshot._stash_buffer')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_snapshot_noMessage(self, mock_swallow, mock_call, mock_stashbuffer, mock_checkoutput):

        # when
        snapshot.snapshot()

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_stashbuffer.assert_called_once()
        mock_call.assert_called_once_with('git stash push --include-untracked'.split())
        mock_swallow.assert_called_once_with('git stash apply --quiet --index'.split())

    @mock.patch('subprocess.check_output', return_value='status\noutput\n')
    @mock.patch('bin.commands.snapshot._stash_buffer')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_snapshot_quiet(self, mock_swallow, mock_call, mock_stashbuffer, mock_checkoutput):

        # when
        snapshot.snapshot(quiet=True)

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_stashbuffer.assert_called_once()
        mock_call.assert_called_once_with('git stash push --include-untracked --quiet'.split())
        mock_swallow.assert_called_once_with('git stash apply --quiet --index'.split())

    @mock.patch('subprocess.check_output', return_value='status\noutput\n')
    @mock.patch('bin.commands.snapshot._stash_buffer')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_snapshot_withMessage(self, mock_swallow, mock_call, mock_stashbuffer, mock_checkoutput):

        # when
        message = 'the message'
        snapshot.snapshot(message)

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_stashbuffer.assert_called_once()
        mock_call.assert_called_once_with(['git', 'stash', 'push', '--include-untracked', '--message', message])
        mock_swallow.assert_called_once_with('git stash apply --quiet --index'.split())

    @mock.patch('subprocess.check_output', return_value='status\noutput\n')
    @mock.patch('bin.commands.snapshot._stash_buffer')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_snapshot_withFiles(self, mock_swallow, mock_call, mock_stashbuffer, mock_checkoutput):

        # when
        message = None
        files = ['file1', 'file2']
        snapshot.snapshot(message, files=files)

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_stashbuffer.assert_called_once()
        mock_call.assert_called_once_with(['git', 'stash', 'push', '--include-untracked', '--'] + files)
        mock_swallow.assert_called_once_with('git stash apply --quiet --index'.split())

    @mock.patch('subprocess.check_output', return_value='status\noutput\n')
    @mock.patch('bin.commands.snapshot._stash_buffer')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_snapshot_withFilesAndMessages(self, mock_swallow, mock_call, mock_stashbuffer, mock_checkoutput):

        # when
        message = 'the message'
        files = ['file1', 'file2']
        snapshot.snapshot(message, files=files)

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_stashbuffer.assert_called_once()
        mock_call.assert_called_once_with(['git', 'stash', 'push', '--include-untracked', '--message', message, '--'] + files)
        mock_swallow.assert_called_once_with('git stash apply --quiet --index'.split())

    @mock.patch('subprocess.check_output', return_value='')
    @mock.patch('bin.commands.utils.messages.info')
    def test_snapshot_noChangesToSnapshot(self, mock_info, mock_checkoutput):

        # when
        quiet = False
        snapshot.snapshot(quiet=quiet)

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_info.assert_called_once_with('No local changes to save. No snapshot created.', quiet)

    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.snapshot._stash_buffer')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_snapshot_replace(self, mock_swallow, mock_call, mock_stashbuffer, mock_checkoutput):

        # given
        mock_checkoutput.side_effect = [
            'status\noutput\n',
            'stash@{0}: WIP on master: 8a3a15e edit readme\nstash@{1}: On master: edit readme\n'
        ]

        # when
        snapshot.snapshot('edit readme', replace=True)

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git status --porcelain'.split()),
            mock.call('git stash list'.split())
        ])
        mock_stashbuffer.assert_called_once()
        mock_call.assert_has_calls([
            mock.call('git stash drop --quiet stash@{1}'.split()),
            mock.call(['git', 'stash', 'push', '--include-untracked', '--message', 'edit readme'])
        ])
        mock_swallow.assert_called_once_with('git stash apply --quiet --index'.split())

    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.snapshot._stash_buffer')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_snapshot_replace_nothingMatches(self, mock_swallow, mock_call, mock_stashbuffer, mock_checkoutput):
        # given
        mock_checkoutput.side_effect = [
            'status\noutput\n',
            'stash@{0}: WIP on master: 8a3a15e edit readme\n'
        ]

        # when
        snapshot.snapshot('edit readme', replace=True)

        # then
        mock_checkoutput.assert_has_calls([
            mock.call('git status --porcelain'.split()),
            mock.call('git stash list'.split())
        ])
        mock_stashbuffer.assert_called_once()
        mock_call.assert_called_once_with(['git', 'stash', 'push', '--include-untracked', '--message', 'edit readme'])
        mock_swallow.assert_called_once_with('git stash apply --quiet --index'.split())

    @mock.patch('subprocess.check_output', return_value='status\noutput\n')
    @mock.patch('bin.commands.snapshot._stash_buffer')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_snapshot_replace_noMessageIncluded(self, mock_swallow, mock_call, mock_stashbuffer, mock_checkoutput):

        # when
        snapshot.snapshot(replace=True)

        # then
        mock_checkoutput.assert_called_once_with('git status --porcelain'.split())
        mock_stashbuffer.assert_called_once()
        mock_call.assert_called_once_with('git stash push --include-untracked'.split())
        mock_swallow.assert_called_once_with('git stash apply --quiet --index'.split())


class TestSnapshotStashBuffer(unittest.TestCase):

    @mock.patch('subprocess.check_output', return_value='\n')
    def test_snapshot_stashBuffer_noPreviousStashes(self, mock_checkoutput):

        # when
        snapshot._stash_buffer(False)

        # then
        mock_checkoutput.assert_called_once_with(('git', 'stash', 'list'))

    @mock.patch('subprocess.check_output')
    @mock.patch('time.strftime')
    def test_snapshot_stashBuffer_previousStashesButNoConflict(self, mock_strftime, mock_checkoutput):

        # given
        mock_checkoutput.side_effect = ['stash0\n', 'time1']
        mock_strftime.return_value = 'time0'

        # when
        snapshot._stash_buffer(True)

        # then
        mock_checkoutput.assert_has_calls([
            mock.call(('git', 'stash', 'list')),
            mock.call(('git', 'show', '-s', '--format=%ci', 'stash@{0}'))
        ])
        mock_strftime.assert_called_once_with('%Y-%m-%d %H:%M:%S %z')

    @mock.patch('subprocess.check_output')
    @mock.patch('time.strftime')
    @mock.patch('bin.commands.utils.messages.warn', return_value=True)
    def test_snapshot_stashBuffer_conflictFound(self, mock_warn, mock_strftime, mock_checkoutput):

        # given
        mock_checkoutput.side_effect = ['stash0\n', 'time0']
        mock_strftime.side_effect = ['time0', 'time0', 'time1']
        quiet = True

        # when
        snapshot._stash_buffer(quiet)

        # then
        mock_checkoutput.assert_has_calls([
            mock.call(('git', 'stash', 'list')),
            mock.call(('git', 'show', '-s', '--format=%ci', 'stash@{0}'))
        ])
        mock_strftime.assert_called_with('%Y-%m-%d %H:%M:%S %z')
        self.assertEqual(mock_strftime.call_count, 3)
        mock_warn.assert_has_calls([
            mock.call('snapshot created too close to last stash', quiet=quiet, ignore=False),
            mock.call('snapshot created too close to last stash', quiet=quiet, ignore=True)
        ])
