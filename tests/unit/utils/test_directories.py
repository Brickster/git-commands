import os
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

    @mock.patch('os.getcwd')
    @mock.patch('bin.commands.utils.directories.is_git_repository')
    @mock.patch('bin.commands.utils.messages.error')
    def test_exitIfNotGitRepository_noDirectoryGiven(self, mock_error, mock_is_git_repository, mock_getcwd):

        # given
        directory = '/repo/path'
        mock_getcwd.return_value = directory
        mock_is_git_repository.return_value = True

        # when
        directories.exit_if_not_git_repository()

        # then
        mock_getcwd.assert_called_once_with()
        mock_is_git_repository.assert_called_once_with(directory)
        mock_error.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository')
    @mock.patch('bin.commands.utils.messages.error')
    def test_exitIfNotGitRepository_isGitRepository(self, mock_error, mock_is_git_repository):

        # given
        directory = '/repo/path'
        mock_is_git_repository.return_value = True

        # when
        directories.exit_if_not_git_repository(directory)

        # then
        mock_is_git_repository.assert_called_once_with(directory)
        mock_error.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository')
    @mock.patch('bin.commands.utils.messages.error')
    def test_exitIfNotGitRepository_notAGitRepository(self, mock_error, mock_is_git_repository):

        # given
        directory = '/repo/path'
        mock_is_git_repository.return_value = False

        # when
        directories.exit_if_not_git_repository(directory)

        # then
        mock_is_git_repository.assert_called_once()
        mock_error.assert_called_once_with('{0!r} not a git repository'.format(directory))
