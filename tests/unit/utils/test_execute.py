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
