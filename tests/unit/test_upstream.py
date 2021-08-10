import unittest
import mock

from . import testutils
from bin.commands import upstream


@mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
class TestUpstream(unittest.TestCase):

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('bin.commands.utils.execute.stdout')
    def test_upstream(self, mock_stdout, mock_currentbranch, mock_isemptyrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)
        mock_stdout.return_value = upstream_info

        # when
        actual_upstream = upstream.upstream()

        # then
        self.assertEqual(actual_upstream, expected_upstream)

        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()
        mock_stdout.assert_called_once_with('git config --local branch.the-branch.merge')

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('bin.commands.utils.execute.stdout')
    def test_upstream_includeRemote_noUpstream(self, mock_stdout, mock_currentbranch, mock_isemptyrepository):

        # setup
        mock_stdout.return_value = ''

        # when
        actual_upstream = upstream.upstream()

        # then
        self.assertEqual(actual_upstream, '')

        mock_currentbranch.assert_called_once_with()
        mock_stdout.assert_called_once_with('git config --local branch.the-branch.merge')

    def test_upstream_repositoryIsEmpty(self, mock_isemptyrepository):

        # setup
        mock_isemptyrepository.return_value = True

        # when
        upstream_result = upstream.upstream()

        # then
        self.assertEqual(upstream_result, None)
        mock_isemptyrepository.assert_called_once_with()


    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('bin.commands.utils.git.is_valid_reference', return_value=True)
    @mock.patch('bin.commands.utils.execute.stdout')
    def test_upstream_branchIncluded(self, mock_stdout, mock_isvalidreference, mock_currentbranch, mock_isemptyrepository):

        # setup
        branch_name = 'the-branch'
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)
        mock_stdout.return_value = upstream_info

        # when
        actual_upstream = upstream.upstream(branch=branch_name)

        # then
        self.assertEqual(actual_upstream, expected_upstream)

        mock_currentbranch.assert_not_called()
        mock_isvalidreference.assert_called_once_with(branch_name)
        mock_stdout.assert_called_once_with('git config --local branch.the-branch.merge')

    @mock.patch('bin.commands.utils.git.is_valid_reference', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_upstream_notAValidReference(self, mock_error, mock_isvalidreference, mock_isemptyrepository):

        # when
        try:
            upstream.upstream(branch='bad-branch')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        mock_isvalidreference.assert_called_once_with('bad-branch')
        mock_error.assert_called_once_with("'bad-branch' is not a valid branch")

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('bin.commands.utils.execute.stdout')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='the-remote')
    def test_upstream_includeRemote_always(self, mock_checkoutput, mock_stdout, mock_currentbranch, mock_isemptyrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)
        mock_stdout.return_value = upstream_info

        # when
        actual_upstream = upstream.upstream(include_remote=upstream.IncludeRemote.ALWAYS)

        # then
        self.assertEqual(actual_upstream, 'the-remote/' + expected_upstream)

        mock_isemptyrepository.assert_called_once()
        mock_currentbranch.assert_called_once()
        mock_stdout.assert_called_once_with('git config --local branch.the-branch.merge')
        mock_checkoutput.assert_called_once_with('git config --local branch.the-branch.remote')

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('bin.commands.utils.execute.stdout')
    def test_upstream_includeRemote_never(self, mock_stdout, mock_currentbranch, mock_isemptyrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)
        mock_stdout.return_value = upstream_info

        # when
        actual_upstream = upstream.upstream(include_remote=upstream.IncludeRemote.NEVER)

        # then
        self.assertEqual(actual_upstream, expected_upstream)

        mock_isemptyrepository.assert_called_once()
        mock_currentbranch.assert_called_once()
        mock_stdout.assert_called_once_with('git config --local branch.the-branch.merge')

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('bin.commands.utils.execute.stdout')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='the-remote')
    def test_upstream_includeRemote_noneLocal_notLocal(self, mock_checkoutput, mock_stdout, mock_currentbranch, mock_isemptyrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)
        mock_stdout.return_value = upstream_info

        # when
        actual_upstream = upstream.upstream(include_remote=upstream.IncludeRemote.NONE_LOCAL)

        # then
        self.assertEqual(actual_upstream, 'the-remote/' + expected_upstream)

        mock_isemptyrepository.assert_called_once()
        mock_currentbranch.assert_called_once()
        mock_stdout.assert_called_once_with('git config --local branch.the-branch.merge')
        mock_checkoutput.assert_called_once_with('git config --local branch.the-branch.remote')

    @mock.patch('bin.commands.utils.git.current_branch', return_value='the-branch')
    @mock.patch('bin.commands.utils.execute.stdout')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='.')
    def test_upstream_includeRemote_noneLocal_isLocal(self, mock_checkoutput, mock_stdout, mock_currentbranch, mock_isemptyrepository):

        # setup
        expected_upstream = "the-upstream"
        upstream_info = "refs/heads/{}\n".format(expected_upstream)
        mock_stdout.return_value = upstream_info

        # when
        actual_upstream = upstream.upstream(include_remote=upstream.IncludeRemote.NONE_LOCAL)

        # then
        self.assertEqual(actual_upstream, expected_upstream)

        mock_isemptyrepository.assert_called_once()
        mock_currentbranch.assert_called_once()
        mock_stdout.assert_called_once_with('git config --local branch.the-branch.merge')
        mock_checkoutput.assert_called_once_with('git config --local branch.the-branch.remote')
