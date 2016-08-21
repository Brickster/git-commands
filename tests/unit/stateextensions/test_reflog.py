import mock
import unittest

from bin.commands.stateextensions import reflog


class TestReflog(unittest.TestCase):

    def test_title(self):
        self.assertEqual(reflog.title(), 'reflog')

    def test_accent(self):
        self.assertEqual(reflog.accent(), None)

    @mock.patch('subprocess.check_output')
    def test_get(self, mock_checkoutput):

        # setup
        expected_reflog = 'expected reflog'
        mock_checkoutput.return_value = expected_reflog

        # when
        reflog_count = 3
        show_color = 'auto'
        actual_reflog = reflog.get(reflog_count=reflog_count, show_color=show_color)

        # then
        self.assertEqual(actual_reflog, expected_reflog)
        mock_checkoutput.assert_called_once_with(
            ['git', 'reflog', '-n', str(reflog_count), '--color=' + show_color]
        )