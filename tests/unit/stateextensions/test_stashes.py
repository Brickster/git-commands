import mock
import unittest

from bin.commands.stateextensions import stashes


class TestStashes(unittest.TestCase):

    def test_title(self):
        self.assertEqual(stashes.title(), 'stashes')

    def test_accent(self):
        self.assertEqual(stashes.accent(), None)

    @mock.patch('subprocess.check_output')
    def test_get(self, mock_checkoutput):

        # setup
        expected_stashes = 'expected stashes'
        mock_checkoutput.return_value = expected_stashes

        # when
        show_color = 'auto'
        actual_stashes = stashes.get(show_color=show_color)

        # then
        self.assertEqual(actual_stashes, expected_stashes)
        mock_checkoutput.assert_called_once_with(['git', 'stash', 'list', '--oneline', '--color=' + show_color])