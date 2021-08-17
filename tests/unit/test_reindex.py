import mock
import unittest

from . import testutils
from ..layers import GitReindex
from bin.commands import reindex


class TestReindex(unittest.TestCase):
    layer = GitReindex

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.git.deleted_files', return_value=['file3'])
    @mock.patch('bin.commands.utils.execute.call')
    def test_reindex_noneDeleted(self, mock_call, mock_deletedfiles, mock_checkoutput, mock_isgitrepository):

        # setup
        files = ['file1', 'file2']
        mock_checkoutput.return_value = '\n'.join(files) + '\n'

        # when
        reindex.reindex()

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_checkoutput.assert_called_once_with('git diff --name-only --cached'.split())
        mock_call.assert_called_once_with(['git', 'add', '--'] + files)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.git.deleted_files')
    @mock.patch('bin.commands.utils.execute.call')
    def test_reindex_someDeleted(self, mock_call, mock_deletedfiles, mock_checkoutput, mock_isgitrepository):

        # setup
        files = ['file1', 'file2', 'file3']
        mock_checkoutput.return_value = '\n'.join(files) + '\n'
        mock_deletedfiles.return_value = ['file2']

        # when
        reindex.reindex()

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_checkoutput.assert_called_once_with('git diff --name-only --cached'.split())
        mock_call.assert_called_once_with(['git', 'add', '--', 'file1', 'file3'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.git.deleted_files')
    @mock.patch('bin.commands.utils.execute.call')
    def test_reindex_allDeleted(self, mock_call, mock_deletedfiles, mock_checkoutput, mock_isgitrepository):

        # setup
        files = ['file1', 'file2']
        mock_checkoutput.return_value = '\n'.join(files) + '\n'
        mock_deletedfiles.return_value = files

        # when
        reindex.reindex()

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_checkoutput.assert_called_once_with('git diff --name-only --cached'.split())
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output', return_value = '')
    @mock.patch('bin.commands.utils.execute.call')
    def test_reindex_noFilesToIndex(self, mock_call, mock_checkoutput, mock_isgitrepository):

        # when
        reindex.reindex()

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_checkoutput.assert_called_once_with('git diff --name-only --cached'.split())
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test_reindex_notAGitRepository(self, mock_getcwd, mock_error, mock_isgitrepository):

        # when
        try:
            reindex.reindex()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_error.assert_called_once_with("'/working/dir' not a git repository")
        mock_getcwd.assert_called_once_with()
