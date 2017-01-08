import mock
import unittest

from bin.commands.utils import directories


class TestDirectories(unittest.TestCase):

    @mock.patch('os.path.exists', return_value=True)
    def test_isGitRepository(self, mock_exists):

        # given
        directory = '/here'

        # when
        actual = directories.is_git_repository(directory)

        # then
        self.assertTrue(actual)
        mock_exists.assert_called_once_with(directory + '/.git')

    @mock.patch('os.path.exists', return_value=True)
    def test_isGitRepository_withTrailingSlash(self, mock_exists):

        # given
        directory = '/here'

        # when
        actual = directories.is_git_repository(directory + '/')

        # then
        self.assertTrue(actual)
        mock_exists.assert_called_once_with(directory + '/.git')
