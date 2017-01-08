import mock
import sys
import unittest

from bin.commands.utils import messages


class TestMessages(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._print = messages._print

    def tearDown(self):
        messages._print = self._print

    @mock.patch('__builtin__.print')
    def test__print(self, mock_print):

        # given
        message = 'message'
        prefix = 'a prefix:'
        quiet = False
        exit_ = False
        file_ = sys.stdout

        # then
        messages._print(message, prefix, quiet, exit_, file_)

        # then
        mock_print.assert_called_once_with(prefix + ' ' + message, file=file_)

    @mock.patch('__builtin__.print')
    def test__print_quiet(self, mock_print):

        # given
        message = 'message'
        prefix = 'a prefix:'
        quiet = True
        exit_ = False
        file_ = sys.stdout

        # then
        messages._print(message, prefix, quiet, exit_, file_)

        # then
        mock_print.assert_not_called()

    @mock.patch('__builtin__.print')
    def test__print_andExit(self, mock_print):

        # given
        message = 'message'
        prefix = 'a prefix:'
        quiet = False
        exit_ = True
        file_ = sys.stdout

        # then
        try:
            messages._print(message, prefix, quiet, exit_, file_)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_print.assert_called_once_with(prefix + ' ' + message, file=file_)

    def test__print_messageNotAStr(self):

        # when
        with self.assertRaises(AssertionError) as context:
            messages._print(123)

        # then
        self.assertEqual(context.exception.message, 'message must be a str')

    def test__print_prefixNotAStr(self):

        # when
        with self.assertRaises(AssertionError) as context:
            messages._print('message', prefix=123)

        # then
        self.assertEqual(context.exception.message, 'prefix must be a str')

    def test__print_quietNotABool(self):

        # when
        with self.assertRaises(AssertionError) as context:
            messages._print('message', quiet='false')

        # then
        self.assertEqual(context.exception.message, 'quiet must be a bool')

    def test__print_exitNotABool(self):

        # when
        with self.assertRaises(AssertionError) as context:
            messages._print('message', exit_='false')

        # then
        self.assertEqual(context.exception.message, 'exit must be a bool')

    @mock.patch('bin.commands.utils.messages._print')
    def test_error(self, mock_print):

        # given
        message = 'the message'
        prefix = 'error prefix'
        exit_ = False

        # when
        messages.error(message, prefix=prefix, exit_=exit_)

        # then
        mock_print.assert_called_once_with(message, prefix=prefix, exit_=exit_, file_=sys.stderr)

    @mock.patch('bin.commands.utils.messages._print')
    def test_warn(self, mock_print):

        # given
        message = 'the message'

        # when
        messages.warn(message)

        # then
        mock_print.assert_called_once_with(message, prefix='warn:')

    @mock.patch('bin.commands.utils.messages._print')
    def test_usage(self, mock_print):

        # given
        message = 'the message'

        # when
        messages.usage(message)

        # then
        mock_print.assert_called_once_with(message, prefix='usage:')

    @mock.patch('bin.commands.utils.messages._print')
    def test_info(self, mock_print):

        # given
        message = 'the message'
        quiet = True

        # when
        messages.info(message, quiet)

        # then
        mock_print.assert_called_once_with(message, quiet=quiet)