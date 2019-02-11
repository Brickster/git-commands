import os
import mock
import subprocess
import unittest

from bin.commands.utils import execute


class TestExecute(unittest.TestCase):

    @mock.patch('subprocess.call')
    def test_swallow(self, mock_call):

        # given
        command = 'git commit'.split()

        # when
        execute.swallow(command)

        # then
        mock_call.assert_called_once_with(command, stdout=mock.ANY, stderr=subprocess.STDOUT)
        self.assertEqual(mock_call.call_args[1]['stdout'].name, os.devnull)

    @mock.patch('subprocess.Popen')
    def test_stdout(self, mock_popen):

        # given
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = ['testing' + os.linesep]

        command = ('git', 'config', '--list')

        # when
        stdout = execute.stdout(command)

        # then
        mock_popen.assert_called_once_with(command, stdout=subprocess.PIPE, stderr=mock.ANY)
        self.assertEqual(mock_popen.call_args[1]['stderr'].name, os.devnull)

        stdout == 'testing' + os.linesep
