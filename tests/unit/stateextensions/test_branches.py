import mock
import re
import unittest

from bin.commands import settings
from bin.commands.stateextensions import branches

_ONLY_DEFAULT_KEY = 'git-state.branches.show-only-default'
_DEFAULT_KEY = 'git-state.branches.default'


class TestBranches(unittest.TestCase):

    def setUp(self):
        # store _only_default_branch so it can be restored after tests that mock it
        self._only_default_branch = branches._only_default_branch

    def tearDown(self):
        branches._only_default_branch = self._only_default_branch

    def test_title(self):
        self.assertEqual(branches.title(), 'branches')

    def test_accent(self):
        self.assertEqual(branches.accent(), None)

    @mock.patch('subprocess.check_output', return_value='one\n')
    @mock.patch('bin.commands.settings.get', return_value='master')
    @mock.patch('re.match', return_value=re.match('a', 'a'))
    def test_onlyDefaultBranch(self, mock_match, mock_get, mock_checkoutput):

        # when
        actual_result = branches._only_default_branch()

        # then
        self.assertEqual(actual_result, True)

        mock_checkoutput.assert_called_once_with('git branch --no-color'.split())
        mock_get.assert_called_once_with(_DEFAULT_KEY, default='master')
        mock_match.assert_called_once_with('\* master', 'one')

    @mock.patch('subprocess.check_output', return_value='one\ntwo\n')
    @mock.patch('bin.commands.settings.get')
    @mock.patch('re.match')
    def test_onlyDefaultBranch_branchCountGreaterThanOne(self, mock_match, mock_get, mock_checkoutput):

        # when
        actual_result = branches._only_default_branch()

        # then
        self.assertEqual(actual_result, False)

        mock_checkoutput.assert_called_once_with('git branch --no-color'.split())
        mock_get.assert_not_called()
        mock_match.assert_not_called()

    @mock.patch('bin.commands.settings.get', return_value=True)
    @mock.patch('subprocess.check_output')
    def test_get_showOnlyDefaultBranch(self, mock_checkoutput, mock_get):

        # setup
        mock_onlydefaultbranch = mock.Mock()
        branches._only_default_branch = mock_onlydefaultbranch
        expected_output = 'the branches output'
        mock_checkoutput.return_value = expected_output

        # when
        show_color = 'always'
        actual_output = branches.get(show_color=show_color)

        # then
        self.assertEqual(actual_output, expected_output)

        mock_get.assert_called_once_with(_ONLY_DEFAULT_KEY, default=True, as_type=settings.as_bool)
        mock_checkoutput.assert_called_once_with(['git', 'branch', '-vv', '--color={}'.format(show_color)])
        mock_onlydefaultbranch.assert_not_called()

    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('subprocess.check_output')
    def test_get_notShowOnlyDefaultBranch_butMoreThanJustDefaultBranch(self, mock_checkoutput, mock_get):

        # setup
        mock_onlydefaultbranch = mock.Mock()
        mock_onlydefaultbranch.return_value = False
        branches._only_default_branch = mock_onlydefaultbranch
        expected_output = 'the branches output'
        mock_checkoutput.return_value = expected_output

        # when
        show_color = 'always'
        actual_output = branches.get(show_color=show_color)

        # then
        self.assertEqual(actual_output, expected_output)

        mock_get.assert_called_once_with(_ONLY_DEFAULT_KEY, default=True, as_type=settings.as_bool)
        mock_checkoutput.assert_called_once_with(['git', 'branch', '-vv', '--color={}'.format(show_color)])

    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('subprocess.check_output')
    def test_get_notShowOnlyDefaultBranch_andOnlyDefaultBranch(self, mock_checkoutput, mock_get):

        # setup
        mock_onlydefaultbranch = mock.Mock()
        mock_onlydefaultbranch.return_value = True
        branches._only_default_branch = mock_onlydefaultbranch

        # when
        show_color = 'always'
        actual_output = branches.get(show_color=show_color)

        # then
        self.assertEqual(actual_output, None)

        mock_get.assert_called_once_with(_ONLY_DEFAULT_KEY, default=True, as_type=settings.as_bool)
        mock_checkoutput.assert_not_called()
