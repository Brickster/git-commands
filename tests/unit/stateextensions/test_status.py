import mock
import os
import unittest

from colorama import Fore

from ...layers import GitStateExtensions
from bin.commands.stateextensions import status


class TestStatus(unittest.TestCase):
    layer = GitStateExtensions

    def test_title(self):
        self.assertEqual(status.title(), 'status')

    def test_accent_newRepository(self):

        # when
        actual_status = status.accent(new_repository=True, show_color='auto')

        # then
        self.assertEqual(
            actual_status,
            '{no_color}({green}master{no_color})'.format(no_color=Fore.RESET, green=Fore.GREEN)
        )

    @mock.patch('bin.commands.utils.execute.check_output', return_value='the full title\n')
    @mock.patch('re.match')
    def test_accent_notNewRepository(self, mock_rematch, mock_checkoutput):

        # setup
        mock_match = mock.Mock()
        mock_match.group = mock.Mock()
        mock_match.group.return_value = 'the short title'
        mock_rematch.return_value = mock_match

        # when
        show_color = 'always'
        actual_status = status.accent(new_repository=False, show_color=show_color)

        # then
        self.assertEqual(actual_status, '{}({})'.format(Fore.RESET, 'the short title'))

        mock_checkoutput.assert_called_once_with(
            ['git', '-c', 'color.status=' + show_color, 'status', '--branch', '--short']
        )
        mock_rematch.assert_called_once_with('.*##.*? (.*)', 'the full title')
        mock_match.group.assert_called_once_with(1)

    @mock.patch('bin.commands.utils.execute.check_output', return_value='the full title\n')
    @mock.patch('re.match')
    def test_accent_notNewRepository_butNotPassedInAsArgument(self, mock_rematch, mock_checkoutput):

        # setup
        mock_match = mock.Mock()
        mock_match.group = mock.Mock()
        mock_match.group.return_value = 'the short title'
        mock_rematch.return_value = mock_match

        # when
        show_color = 'always'
        actual_status = status.accent(show_color=show_color)

        # then
        self.assertEqual(actual_status, '{}({})'.format(Fore.RESET, 'the short title'))

        mock_checkoutput.assert_called_once_with(
            ['git', '-c', 'color.status=' + show_color, 'status', '--branch', '--short']
        )
        mock_rematch.assert_called_once_with('.*##.*? (.*)', 'the full title')
        mock_match.group.assert_called_once_with(1)

    @mock.patch('bin.commands.utils.execute.check_output', return_value='the status')
    def test_get_newRepository(self, mock_checkoutput):

        # when
        show_color = 'always'
        actual_status = status.get(new_repository=True, show_color=show_color)

        # then
        self.assertEqual(actual_status, 'the status')
        mock_checkoutput.assert_called_once_with(['git', '-c', 'color.status=' + show_color, 'status', '--short'])

    @mock.patch('bin.commands.utils.execute.check_output', return_value='')
    def test_get_newRepository_repositoryIsEmpty(self, mock_checkoutput):

        # when
        show_color = 'always'
        actual_status = status.get(new_repository=True, show_color=show_color)

        # then
        self.assertEqual(actual_status, 'nothing to commit, repository is empty' + os.linesep)
        mock_checkoutput.assert_called_once_with(['git', '-c', 'color.status=' + show_color, 'status', '--short'])

    @mock.patch('bin.commands.utils.execute.check_output', return_value='the status')
    def test_get_notNewRepository(self, mock_checkoutput):

        # when
        show_color = 'auto'
        actual_status = status.get(show_color=show_color)

        # then
        self.assertEqual(actual_status, 'the status')
        mock_checkoutput.assert_called_once_with(
            ['git', '-c', 'color.status=' + show_color, 'status', '--short', '--untracked-files=all']
        )

    @mock.patch('bin.commands.utils.execute.check_output', return_value='')
    def test_get_notNewRepository_noStatus_andShowCleanMessage(self, mock_checkoutput):

        # when
        show_color = 'auto'
        actual_status = status.get(show_color=show_color, show_clean_message=True)

        # then
        self.assertEqual(actual_status, 'nothing to commit, working directory is clean' + os.linesep)
        mock_checkoutput.assert_called_once_with(
            ['git', '-c', 'color.status=' + show_color, 'status', '--short', '--untracked-files=all']
        )

    @mock.patch('bin.commands.utils.execute.check_output', return_value='')
    def test_get_notNewRepository_noStatus_andNoShowCleanMessage(self, mock_checkoutput):

        # when
        show_color = 'auto'
        actual_status = status.get(show_color=show_color, show_clean_message=False)

        # then
        self.assertEqual(actual_status, '')
        mock_checkoutput.assert_called_once_with(
            ['git', '-c', 'color.status=' + show_color, 'status', '--short', '--untracked-files=all']
        )
