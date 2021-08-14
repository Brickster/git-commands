import os
import mock
import subprocess
import unittest
from builtins import bytes

from bin.commands.utils import execute


class TestExecute(unittest.TestCase):

    @mock.patch('subprocess.call')
    def test_swallow(self, mock_call):

        # given
        command = 'git commit'.split()

        # when
        execute.swallow(command)

        # then
        mock_call.assert_called_once_with(command, stdout=mock.ANY, stderr=mock.ANY)
        self.assertEqual(mock_call.call_args[1]['stdout'].name, os.devnull)

    @mock.patch('subprocess.call')
    def test_swallow_asStr(self, mock_call):

        # given
        command = 'git commit'

        # when
        execute.swallow(command)

        # then
        mock_call.assert_called_once_with(command.split(), stdout=mock.ANY, stderr=mock.ANY)
        self.assertEqual(mock_call.call_args[1]['stdout'].name, os.devnull)

    @mock.patch('subprocess.Popen')
    def test_stdout(self, mock_popen):

        # given
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = [bytes('testing' + os.linesep, 'utf-8')]

        command = ['git', 'config', '--list']

        # when
        stdout = execute.stdout(command)

        # then
        mock_popen.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=mock.ANY)
        self.assertEqual(mock_popen.call_args[1]['stderr'].name, os.devnull)

        stdout == 'testing' + os.linesep

    @mock.patch('subprocess.Popen')
    def test_stdout_asStr(self, mock_popen):

        # given
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = [bytes('testing' + os.linesep, 'utf-8')]

        command = 'git config --list'

        # when
        stdout = execute.stdout(command)

        # then
        mock_popen.assert_called_once_with(command.split(), stdout=subprocess.PIPE, stderr=mock.ANY)
        self.assertEqual(mock_popen.call_args[1]['stderr'].name, os.devnull)

        stdout == 'testing' + os.linesep

    @mock.patch('subprocess.Popen')
    def test_call_input(self, mock_popen):

        # given
        command = 'the command'.split()
        the_input = '123'

        mock_process = mock.Mock()
        mock_process.communicate = mock.Mock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # when
        return_code = execute.call_input(command, the_input)

        # then
        mock_popen.assert_called_once_with(command, stdin=subprocess.PIPE)
        mock_process.communicate.assert_called_once_with(input=the_input.encode('utf-8'))

        self.assertEqual(return_code, 0)

    @mock.patch('subprocess.Popen')
    def test_call_input_asStr(self, mock_popen):
        # given
        command = 'the command'
        the_input = '123'

        mock_process = mock.Mock()
        mock_process.communicate = mock.Mock()
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        # when
        return_code = execute.call_input(command, the_input)

        # then
        mock_popen.assert_called_once_with(command.split(), stdin=subprocess.PIPE)
        mock_process.communicate.assert_called_once_with(input=the_input.encode('utf-8'))

        self.assertEqual(return_code, 0)

    @mock.patch('subprocess.Popen')
    def test_execute(self, mock_popen):

        # given
        command = 'the command'.split()
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [b'the stdout', b'the stderr']
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        # when
        actual_stdout, actual_stderr, actual_return_code = execute.execute(command)

        # then
        mock_popen.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mock_proc.communicate.assert_called_once()

        self.assertEqual(actual_stdout, 'the stdout')
        self.assertEqual(actual_stderr, 'the stderr')
        self.assertEqual(actual_return_code, 0)

    @mock.patch('subprocess.Popen')
    def test_execute_asStr(self, mock_popen):

        # given
        command = 'the command'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [b'the stdout', b'the stderr']
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        # when
        actual_stdout, actual_stderr, actual_return_code = execute.execute(command)

        # then
        mock_popen.assert_called_once_with(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mock_proc.communicate.assert_called_once()

        self.assertEqual(actual_stdout, 'the stdout')
        self.assertEqual(actual_stderr, 'the stderr')
        self.assertEqual(actual_return_code, 0)

    @mock.patch('subprocess.check_output')
    def test_checkout(self, mock_checkoutput):

        # given
        command = ['the', 'command']
        mock_checkoutput.return_value = b'the output'

        # when
        output = execute.check_output(command)

        # then
        mock_checkoutput.assert_called_once_with(command)
        self.assertEqual('the output', output)

    @mock.patch('subprocess.check_output')
    def test_checkout_asStr(self, mock_checkoutput):

        # given
        command = 'the command'
        mock_checkoutput.return_value = b'the output'

        # when
        output = execute.check_output(command)

        # then
        mock_checkoutput.assert_called_once_with(command.split())
        self.assertEqual('the output', output)

    @mock.patch('subprocess.call')
    def test_call(self, mock_call):

        # given
        command = ['the', 'command']
        mock_call.return_value = 0

        # when
        return_code = execute.call(command)

        # then
        mock_call.assert_called_once_with(command)
        self.assertEqual(0, return_code)

    @mock.patch('subprocess.call')
    def test_call_asStr(self, mock_call):

        # given
        command = 'the command'
        mock_call.return_value = 0

        # when
        return_code = execute.call(command)

        # then
        mock_call.assert_called_once_with(command.split())
        self.assertEqual(0, return_code)

    @mock.patch('subprocess.call')
    @mock.patch('subprocess.Popen')
    def test_pipe(self, mock_popen, mock_call):

        # given
        command1 = 'the command one'.split()
        command2 = 'the command two'.split()

        command1_proc = mock.Mock()
        mock_popen.return_value = command1_proc

        # when
        execute.pipe(command1, command2)

        # then
        mock_popen.assert_called_once_with(command1, stdout=subprocess.PIPE)
        mock_call.assert_called_once_with(command2, stdin=command1_proc.stdout)

    @mock.patch('subprocess.call')
    @mock.patch('subprocess.Popen')
    def test_pipe_asStr(self, mock_popen, mock_call):

        # given
        command1 = 'the command one'
        command2 = 'the command two'

        command1_proc = mock.Mock()
        command1_proc.stdout = 'stdout'
        mock_popen.return_value = command1_proc

        # when
        execute.pipe(command1, command2)

        # then
        mock_popen.assert_called_once_with(command1.split(), stdout=subprocess.PIPE)
        mock_call.assert_called_once_with(command2.split(), stdin=command1_proc.stdout)
