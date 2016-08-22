import mock
import unittest

from bin.commands.stateextensions import log


class TestLog(unittest.TestCase):

    def test_title(self):
        self.assertEqual(log.title(), 'log')

    def test_accent(self):
        self.assertEqual(log.accent(), None)

    @mock.patch('subprocess.check_output')
    def test_get(self, mock_checkoutput):

        # setup
        expected_log = 'expected log'
        mock_checkoutput.return_value = expected_log

        # when
        log_count = 3
        show_color = 'auto'
        actual_log = log.get(log_count=log_count, show_color=show_color)

        # then
        self.assertEqual(actual_log, expected_log)
        mock_checkoutput.assert_called_once_with(
            ['git', 'log', '-n', str(log_count), '--oneline', '--color=' + show_color]
        )