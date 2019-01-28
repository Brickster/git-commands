import mock
import unittest

import testutils
from bin.commands import abandon


class TestAbandon(unittest.TestCase):

    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_abandon(self, mock_info, mock_call, mock_checkoutput):

        #  setup
        existing_stashes = '1\n2\n3\n4'
        stash1 = 'stash1\n'
        stash2 = 'stash2\n'
        mock_checkoutput.side_effect = [existing_stashes, stash1, stash2]

        # when
        start = 1
        end = 3
        abandon.abandon(start, end)

        # then
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'stash', 'list']),
            mock.call(['git', 'rev-parse', 'stash@{1}']),
            mock.call(['git', 'rev-parse', 'stash@{1}'])
        ])
        mock_call.assert_called_with('git stash drop --quiet stash@{{{}}}'.format(start).split())
        self.assertEqual(mock_call.call_count, 2)
        mock_info.assert_has_calls([
            mock.call('Dropped refs/stash@{{{}}} ({})'.format(1, stash1.strip()), False),
            mock.call('Dropped refs/stash@{{{}}} ({})'.format(2, stash2.strip()), False)
        ])

    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_abandon_quiet(self, mock_info, mock_call, mock_checkoutput):

        #  setup
        existing_stashes = '1\n2\n3\n4'
        stash1 = 'stash1\n'
        stash2 = 'stash2\n'
        mock_checkoutput.side_effect = [existing_stashes, stash1, stash2]

        # when
        start = 1
        end = 3
        quiet = True
        abandon.abandon(start, end, quiet=quiet)

        # then
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'stash', 'list']),
            mock.call(['git', 'rev-parse', 'stash@{1}']),
            mock.call(['git', 'rev-parse', 'stash@{1}'])
        ])
        mock_call.assert_called_with('git stash drop --quiet stash@{{{}}}'.format(start).split())
        self.assertEqual(mock_call.call_count, 2)
        mock_info.assert_has_calls([
            mock.call('Dropped refs/stash@{{{}}} ({})'.format(1, stash1.strip()), quiet),
            mock.call('Dropped refs/stash@{{{}}} ({})'.format(2, stash2.strip()), quiet)
        ])

    @mock.patch('subprocess.check_output', return_value='1\n2\n3\n')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_abandon_endLessThanZero(self, mock_error, mock_checkoutput):

        # when
        try:
            abandon.abandon(0, -1)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        mock_error.assert_called_once_with('end cannot be negative')

    @mock.patch('subprocess.check_output', return_value='1\n2\n3\n')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_abandon_endBeforeStart(self, mock_error, mock_checkoutput):

        # when
        try:
            abandon.abandon(10, 2)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        mock_error.assert_called_once_with('end of range cannot come before the start')

    @mock.patch('subprocess.check_output', return_value='one\ntwo')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_abandon_startGreaterThanStashCount(self, mock_error, mock_checkoutput):

        # when
        try:
            abandon.abandon(10, 11)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_checkoutput.assert_called_once_with('git stash list'.split())
        mock_error.assert_has_calls([
            mock.call('start too high', exit_=False),
            mock.call('only 2 stashes exist')
        ])

    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_abandon_endGreaterThanStashCount(self, mock_info, mock_call, mock_checkoutput):

        #  setup
        existing_stashes = '1\n2\n'
        stash1 = 'stash1\n'
        stash2 = 'stash2\n'
        mock_checkoutput.side_effect = [existing_stashes, stash1, stash2]

        # when
        start = 0
        end = 200
        abandon.abandon(start, end)

        # then
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'stash', 'list']),
            mock.call(['git', 'rev-parse', 'stash@{0}']),
            mock.call(['git', 'rev-parse', 'stash@{0}'])
        ])
        mock_call.assert_called_with('git stash drop --quiet stash@{{{}}}'.format(start).split())
        self.assertEqual(mock_call.call_count, 2)
        mock_info.assert_has_calls([
            mock.call('Dropped refs/stash@{{{}}} ({})'.format(0, stash1.strip()), False),
            mock.call('Dropped refs/stash@{{{}}} ({})'.format(1, stash2.strip()), False)
        ])

    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.messages.info')
    def test_abandon_dryRun(self, mock_info, mock_checkoutput):

        #  setup
        existing_stashes = '1\n2\n3\n4'
        stash1 = 'stash1\n'
        stash2 = 'stash2\n'
        mock_checkoutput.side_effect = [existing_stashes, stash1, stash2]

        # when
        start = 1
        end = 3
        abandon.abandon(start, end, dry_run=True)

        # then
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'stash', 'list']),
            mock.call(['git', 'rev-parse', 'stash@{1}']),
            mock.call(['git', 'rev-parse', 'stash@{2}'])
        ])
        mock_info.assert_has_calls([
            mock.call('Would drop refs/stash@{{{}}} ({})'.format(1, stash1.strip())),
            mock.call('Would drop refs/stash@{{{}}} ({})'.format(2, stash2.strip()))
        ])

    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.messages.info')
    def test_abandon_dryRun_quiet(self, mock_info, mock_checkoutput):
        """Same as test_abandon_dryRun since a quiet dry run isn't useful."""

        #  setup
        existing_stashes = '1\n2\n3\n4'
        stash1 = 'stash1\n'
        stash2 = 'stash2\n'
        mock_checkoutput.side_effect = [existing_stashes, stash1, stash2]

        # when
        start = 1
        end = 3
        abandon.abandon(start, end, dry_run=True, quiet=True)

        # then
        mock_checkoutput.assert_has_calls([
            mock.call(['git', 'stash', 'list']),
            mock.call(['git', 'rev-parse', 'stash@{1}']),
            mock.call(['git', 'rev-parse', 'stash@{2}'])
        ])
        mock_info.assert_has_calls([
            mock.call('Would drop refs/stash@{{{}}} ({})'.format(1, stash1.strip())),
            mock.call('Would drop refs/stash@{{{}}} ({})'.format(2, stash2.strip()))
        ])
