import unittest
import mock
from subprocess import PIPE

import testutils
from bin.commands import upstream


@mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
@mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
class TestUpstream(unittest.TestCase):

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('subprocess.Popen')
    def test_upstream(self, mock_popen, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)

        mock_process = mock.Mock()
        mock_process.communicate.return_value = [upstream_info]
        mock_popen.return_value = mock_process

        # when
        actual_upstream = upstream.upstream()

        # then
        self.assertEqual(actual_upstream, expected_upstream)

        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()
        mock_process.communicate.assert_called_once_with()
        mock_popen.assert_called_once_with('git config --local branch.the-branch.merge'.split(), stdout=PIPE)

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('subprocess.Popen')
    def test_upstream_includeRemote_noUpstream(self, mock_popen, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        mock_process = mock.Mock()
        mock_process.communicate.return_value = ['']
        mock_popen.return_value = mock_process

        # when
        actual_upstream = upstream.upstream()

        # then
        self.assertEqual(actual_upstream, '')

        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()
        mock_process.communicate.assert_called_once_with()
        mock_popen.assert_called_once_with('git config --local branch.the-branch.merge'.split(), stdout=PIPE)

    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='working_dir')
    def test_upstream_notAGitRepository(self, mock_getcwd, mock_error, mock_isemptyrepository, mock_isgitrepository):

        # setup
        mock_isgitrepository.return_value = False

        # when
        try:
            upstream.upstream()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_error.assert_called_once_with("'working_dir' not a git repository")
        mock_getcwd.assert_called_once_with()

    def test_upstream_repositoryIsEmpty(self, mock_isemptyrepository, mock_isgitrepository):

        # setup
        mock_isemptyrepository.return_value = True

        # when
        upstream_result = upstream.upstream()

        # then
        self.assertEqual(upstream_result, None)
        mock_isemptyrepository.assert_called_once_with()


    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('bin.commands.utils.git.is_valid_reference', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_upstream_branchIncluded(self, mock_popen, mock_isvalidreference, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        branch_name = 'the-branch'
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)

        mock_process = mock.Mock()
        mock_process.communicate.return_value = [upstream_info]
        mock_popen.return_value = mock_process

        # when
        actual_upstream = upstream.upstream(branch=branch_name)

        # then
        self.assertEqual(actual_upstream, expected_upstream)

        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_isvalidreference.assert_called_once_with(branch_name)
        mock_process.communicate.assert_called_once_with()
        mock_popen.assert_called_once_with('git config --local branch.the-branch.merge'.split(), stdout=PIPE)

    @mock.patch('bin.commands.utils.git.is_valid_reference', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_upstream_notAValidReference(self, mock_error, mock_isvalidreference, mock_isemptyrepository, mock_isgitrepository):

        # when
        try:
            upstream.upstream(branch='bad-branch')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        mock_isgitrepository.assert_called_once_with()
        mock_isvalidreference.assert_called_once_with('bad-branch')
        mock_error.assert_called_once_with("'bad-branch' is not a valid branch")

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('subprocess.Popen')
    @mock.patch('subprocess.check_output', return_value='the-remote')
    def test_upstream_includeRemote_always(self, mock_checkoutput, mock_popen, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)

        mock_process = mock.Mock()
        mock_process.communicate.return_value = [upstream_info]
        mock_popen.return_value = mock_process

        # when
        actual_upstream = upstream.upstream(include_remote=upstream.IncludeRemote.ALWAYS)

        # then
        self.assertEqual(actual_upstream, 'the-remote/' + expected_upstream)

        mock_isemptyrepository.assert_called_once()
        mock_isgitrepository.assert_called_once()
        mock_currentbranch.assert_called_once()
        mock_popen.assert_called_once_with('git config --local branch.the-branch.merge'.split(), stdout=PIPE)
        mock_checkoutput.assert_called_once_with('git config --local branch.the-branch.remote'.split())

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('subprocess.Popen')
    def test_upstream_includeRemote_never(self, mock_popen, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)

        mock_process = mock.Mock()
        mock_process.communicate.return_value = [upstream_info]
        mock_popen.return_value = mock_process

        # when
        actual_upstream = upstream.upstream(include_remote=upstream.IncludeRemote.NEVER)

        # then
        self.assertEqual(actual_upstream, expected_upstream)

        mock_isemptyrepository.assert_called_once()
        mock_isgitrepository.assert_called_once()
        mock_currentbranch.assert_called_once()
        mock_popen.assert_called_once_with('git config --local branch.the-branch.merge'.split(), stdout=PIPE)

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('subprocess.Popen')
    @mock.patch('subprocess.check_output', return_value='the-remote')
    def test_upstream_includeRemote_noneLocal_notLocal(self, mock_checkoutput, mock_popen, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)

        mock_process = mock.Mock()
        mock_process.communicate.return_value = [upstream_info]
        mock_popen.return_value = mock_process

        # when
        actual_upstream = upstream.upstream(include_remote=upstream.IncludeRemote.NONE_LOCAL)

        # then
        self.assertEqual(actual_upstream, 'the-remote/' + expected_upstream)

        mock_isgitrepository.assert_called_once()
        mock_isemptyrepository.assert_called_once()
        mock_currentbranch.assert_called_once()
        mock_popen.assert_called_once_with('git config --local branch.the-branch.merge'.split(), stdout=PIPE)
        mock_checkoutput.assert_called_once_with('git config --local branch.the-branch.remote'.split())

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('subprocess.Popen')
    @mock.patch('subprocess.check_output', return_value='.')
    def test_upstream_includeRemote_noneLocal_isLocal(self, mock_checkoutput, mock_popen, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)

        mock_process = mock.Mock()
        mock_process.communicate.return_value = [upstream_info]
        mock_popen.return_value = mock_process

        # when
        actual_upstream = upstream.upstream(include_remote=upstream.IncludeRemote.NONE_LOCAL)

        # then
        self.assertEqual(actual_upstream, expected_upstream)

        mock_isgitrepository.assert_called_once()
        mock_isemptyrepository.assert_called_once()
        mock_currentbranch.assert_called_once()
        mock_popen.assert_called_once_with('git config --local branch.the-branch.merge'.split(), stdout=PIPE)
        mock_checkoutput.assert_called_once_with('git config --local branch.the-branch.remote'.split())

    def test_upstream_includeRemote_wrongType(self, mock_isemptyrepository, mock_isgitrepository):

        # when
        with self.assertRaises(AssertionError) as context:
            upstream.upstream(include_remote='always')

        # then
        self.assertEqual(context.exception.message, "'include_remote' must be a {!r}. Given {!r}".format(upstream.IncludeRemote, str))
        mock_isgitrepository.assert_not_called()
        mock_isemptyrepository.assert_not_called()
