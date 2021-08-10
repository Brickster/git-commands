import mock
import os
import subprocess
import unittest

import colorama

from . import testutils
from bin.commands import state


class TestStatePrintSection(unittest.TestCase):

    def test_printsection_withaccent(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        accent = 'the accent'
        expected_output = '# ' + colorama.Fore.GREEN + title + ' ' + accent + colorama.Fore.RESET + os.linesep + text

        # when
        section_output = state._print_section(title, accent=accent, text=text, color='always')

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_withoutaccent(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        expected_output = '# ' + colorama.Fore.GREEN + title + colorama.Fore.RESET + os.linesep + text

        # when
        section_output = state._print_section(title, accent=None, text=text, color='always')

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_donotshowempty_notext(self):

        # when
        section_output = state._print_section('title', text=None, show_empty=False, color='always')

        # then
        self.assertEqual(section_output, '')

    def test_printsection_donotshowempty_withtext(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        expected_output = '# ' + colorama.Fore.GREEN + title + colorama.Fore.RESET + os.linesep + text

        # when
        section_output = state._print_section(title, accent=None, text=text, show_empty=False, color='always')

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_showempty_notext(self):

        # given
        expected_output = '# ' + colorama.Fore.GREEN + 'title' + colorama.Fore.RESET + os.linesep

        # when
        section_output = state._print_section('title', text=None, show_empty=True, color='always')

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_prettyandtext(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        expected_output = """# {}{}{}

    the text
    here

""".format(colorama.Fore.GREEN, title, colorama.Fore.RESET)

        # when
        section_output = state._print_section(title, text=text, format_='pretty', color='always')

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_prettyandnotext(self):

        # setup
        title = 'the title'
        expected_output = "# {}{}{}".format(colorama.Fore.GREEN, title, colorama.Fore.RESET) + os.linesep + os.linesep

        # when
        section_output = state._print_section(title, text=None, format_='pretty', show_empty=True, color='always')

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_compact(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        expected_output = '# ' + colorama.Fore.GREEN + title + colorama.Fore.RESET + os.linesep + text

        # when
        section_output = state._print_section(title, text=text, color='always')

        # then
        self.assertEqual(section_output, expected_output)

    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_printsection_unknownformat(self, mock_error):

        # when
        try:
            state._print_section('title', text='text', format_='invalid', color='always')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_error.assert_called_once_with("unknown format 'invalid'")

    @mock.patch('sys.stdout.isatty', return_value=True)
    def test_printsection_color_auto_isatty(self, mock_isatty):

        # given
        expected_output = '# ' + colorama.Fore.GREEN + 'title' + colorama.Fore.RESET + os.linesep

        # when
        section_output = state._print_section('title', text=None, show_empty=True, color='auto')

        # then
        self.assertEqual(section_output, expected_output)

        mock_isatty.assert_called_once_with()

    @mock.patch('sys.stdout.isatty', return_value=False)
    def test_printsection_color_auto_isnotatty(self, mock_isatty):

        # given
        expected_output = '# ' + colorama.Fore.RESET + 'title' + colorama.Fore.RESET + os.linesep

        # when
        section_output = state._print_section('title', text=None, show_empty=True, color='auto')

        # then
        self.assertEqual(section_output, expected_output)

        mock_isatty.assert_called_once_with()

    def test_printsection_color_never(self):

        # given
        expected_output = '# ' + colorama.Fore.RESET + 'title' + colorama.Fore.RESET + os.linesep

        # when
        section_output = state._print_section('title', text=None, show_empty=True, color='never')

        # then
        self.assertEqual(section_output, expected_output)


class TestStateState(unittest.TestCase):

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_status(
            self,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': [],
            'show_empty': True
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_getconfigvalue.side_effect = [True, []]
        mock_list.return_value = ''

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_alloff(
            self,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['status'],
            'show_empty': True
        }

        mock_getconfigvalue.side_effect = [True, []]
        mock_list.return_value = ''

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_not_called()
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_not_called()
        mock_info.assert_not_called()
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test_state_notagitrepository(self, mock_getcwd, mock_error, mock_isgitrepository):

        # when
        try:
            state.state()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_error.assert_called_once_with("'/working/dir' not a git repository")
        mock_getcwd.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('colorama.init')
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_showcolor_never(
            self,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_init,
            mock_resolvecoloring,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'always',
            'format_': format_,
            'clear': False,
            'ignore_extensions': [],
            'show_empty': True
        }

        mock_resolvecoloring.return_value = 'never'
        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_getconfigvalue.side_effect = [True, []]
        mock_list.return_value = ''

        # when
        state.state(**kwargs)

        # then
        mock_statusget.assert_called_once_with(
            clear=False,
            format_='compact',
            ignore_extensions=[],
            show_clean_message=True,
            show_color='never',
            show_empty=True
        )
        mock_isgitrepository.assert_called_once_with()
        mock_resolvecoloring.assert_called_once_with('always')
        mock_init.assert_called_once_with(strip=True)
        mock_isemptyrepository.assert_called_once_with()
        mock_list.return_value = ''
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('colorama.init')
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_showcolor_always(
            self,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_init,
            mock_resolvecoloring,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'auto',
            'format_': format_,
            'clear': False,
            'ignore_extensions': [],
            'show_empty': True
        }

        mock_list.return_value = ''
        mock_resolvecoloring.return_value = 'always'
        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_getconfigvalue.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_statusget.assert_called_once_with(
            clear=False,
            format_='compact',
            ignore_extensions=[],
            show_clean_message=True,
            show_color='always',
            show_empty=True
        )
        mock_isgitrepository.assert_called_once_with()
        mock_resolvecoloring.assert_called_once_with('auto')
        mock_init.assert_called_once_with(strip=False)
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='always'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=True)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_emptyRepository(
            self,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        show_empty = True
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': [],
            'show_empty': show_empty
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'section output\n'
        mock_getconfigvalue.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_not_called()
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('section output')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=True)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_emptyRepository_noShowStatus(
            self,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        show_empty = True
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['status'],
            'show_empty': show_empty
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'section output\n'
        mock_getconfigvalue.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_not_called()
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_not_called()
        mock_checkoutput.assert_not_called()
        mock_info.assert_not_called()
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.utils.execute.execute')
    def test_state_withextensions(
            self,
            mock_execute,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['status'],
            'options': {}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_getconfigvalue.side_effect = [True, True, changes_command, changes_name, [], True, []]
        mock_list.return_value = 'git-state.extensions.changes'
        mock_execute.return_value = [changes_output, None, 0]
        mock_printsection.return_value = 'final changes output\n'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            title=changes_name,
            text=changes_output,
            format_=format_,
            show_empty=None,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.command'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_execute.assert_called_once_with(['changes', 'command', '--color=never'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.utils.execute.execute')
    def test_state_withextensions_doesNotSupportColor(
            self,
            mock_execute,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['status'],
            'options': {}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_getconfigvalue.side_effect = [True, True, changes_command, changes_name, [], False, []]
        mock_list.return_value = 'git-state.extensions.changes'
        mock_execute.return_value = [changes_output, None, 0]
        mock_printsection.return_value = 'final changes output\n'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            title=changes_name,
            text=changes_output,
            format_=format_,
            show_empty=None,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.command'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_execute.assert_called_once_with(['changes', 'command'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.utils.execute.execute')
    def test_state_withextensions_withoptions_fromcommandline(
            self,
            mock_execute,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['status'],
            'options': {'changes': ['--option1', '-o "1 2"']}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_getconfigvalue.side_effect = [True, True, changes_command, changes_name, [], True, []]
        mock_list.return_value = 'git-state.extensions.changes'
        mock_execute.return_value = [changes_output, None, 0]
        mock_printsection.return_value = 'final changes output\n'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            title=changes_name,
            text=changes_output,
            format_=format_,
            show_empty=None,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.command'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_execute.assert_called_once_with(['changes', 'command', '--option1', '-o', '1 2', '--color=never'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.utils.execute.execute')
    def test_state_withextensions_withoptions_fromconfig(
            self,
            mock_execute,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['status'],
            'options': {}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_getconfigvalue.side_effect = [True, True, changes_command, changes_name, ['--option1 -o "1 2"'], True, []]
        mock_list.return_value = 'git-state.extensions.changes'
        mock_execute.return_value = [changes_output, None, 0]
        mock_printsection.return_value = 'final changes output\n'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            title=changes_name,
            text=changes_output,
            format_=format_,
            show_empty=None,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.command'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_execute.assert_called_once_with(['changes', 'command', '--option1', '-o', '1 2', '--color=never'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.utils.execute.execute')
    def test_state_withextensions_withoptions_fromcommandlineandconfig(
            self,
            mock_execute,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['status'],
            'options': {'changes': ['--option1', '-o "1 2"']}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_getconfigvalue.side_effect = [True, True, changes_command, changes_name, ['--option2 true'], True, []]
        mock_list.return_value = 'git-state.extensions.changes'
        mock_execute.return_value = [changes_output, None, 0]
        mock_printsection.return_value = 'final changes output\n'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            title=changes_name,
            text=changes_output,
            format_=format_,
            show_empty=None,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.command'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_execute.assert_called_once_with(['changes', 'command', '--option2', 'true', '--option1', '-o', '1 2', '--color=never'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_withextensions_butignoresome(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['changes', 'status'],
            'options': {}
        }
        mock_getconfigvalue.side_effect = [True, []]
        mock_list.return_value = 'git-state.extentions.changes'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_not_called()
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_not_called()
        mock_info.assert_not_called()
        mock_call.assert_not_called()
        mock_popen.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_withextensions_butignoresome_viaconfig(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['status'],
            'options': {}
        }
        mock_getconfigvalue.side_effect = [True, False, []]
        mock_list.return_value = 'git-state.extensions.changes'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_not_called()
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_not_called()
        mock_info.assert_not_called()
        mock_call.assert_not_called()
        mock_popen.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.utils.execute.execute')
    def test_state_withextensions_ignoredViaConfig_showViaCommandLine(
            self,
            mock_execute,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': ['status'],
            'show_extensions': ['changes'],
            'options': {}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_getconfigvalue.side_effect = [True, changes_command, changes_name, [], True, []]
        mock_list.return_value = 'git-state.extensions.changes'
        mock_execute.return_value = [changes_output, None, 0]
        mock_printsection.return_value = 'final changes output\n'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            title=changes_name,
            text=changes_output,
            format_=format_,
            show_empty=None,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.command'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_execute.assert_called_once_with(['changes', 'command', '--color=never'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.utils.execute.execute')
    def test_state_withorder(
            self,
            mock_execute,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': [],
            'options': {},
            'show_empty': True
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.side_effect = ['status section\n', 'changes section\n']
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_getconfigvalue.side_effect = [True, True, changes_command, changes_name, [], True, ['changes', 'status']]
        mock_list.return_value = 'git-state.extensions.changes'
        mock_execute.return_value = [changes_output, None, 0]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_has_calls([
            mock.call(
                mock_statustitle.return_value,
                mock_statusaccent.return_value,
                mock_statusget.return_value,
                format_,
                show_empty=True,
                color='never'
            ),
            mock.call(
                title=changes_name,
                text=changes_output,
                format_=format_,
                show_empty=True,
                color='never'
            )
        ])
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.command'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('changes section\nstatus section')
        mock_call.assert_not_called()
        mock_execute.assert_called_once_with(['changes', 'command', '--color=never'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_withorder_withunknownsection(
            self,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': [],
            'show_empty': True
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.side_effect = ['status section\n']
        mock_getconfigvalue.side_effect = [True, ['status', 'unknown']]
        mock_list.return_value = ''

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='1')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.utils.execute.pipe')
    def test_state_pageOutput(
            self,
            mock_pipe,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': [],
            'show_empty': True
        }

        mock_list.return_value = ''
        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\ntwo\nthree\nfour\nfive\n'
        mock_getconfigvalue.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_not_called()
        mock_pipe.assert_called_once_with(['echo', 'status section\ntwo\nthree\nfour\nfive'], ['less', '-r'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='1')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_doNotPageOutputEvenIfTooLarge(
            self,
            mock_info,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'clear': False,
            'ignore_extensions': [],
            'page': False,
            'show_empty': True
        }

        mock_list.return_value = ''
        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\ntwo\nthree\nfour\nfive\n'
        mock_getconfigvalue.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section\ntwo\nthree\nfour\nfive')

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('colorama.init')
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('sys.stdout.isatty', return_value=True)
    def test_state_clear(
            self,
            mock_isatty,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_init,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'ignore_extensions': [],
            'clear': True,
            'show_empty': True
        }

        mock_list.return_value = ''
        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_getconfigvalue.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_init.assert_called_once_with(strip=True)
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_called_once_with('clear')

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('sys.stdout.isatty', return_value=False)
    def test_state_clear_notatty(
            self,
            mock_isatty,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'ignore_extensions': [],
            'clear': True,
            'show_empty': True
        }

        mock_list.return_value = ''
        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_getconfigvalue.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections'
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.get_config_value', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.execute.check_output', return_value='100')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_clear_noclear(
            self,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_getconfigvalue,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format_': format_,
            'ignore_extensions': [],
            'clear': False,
            'show_empty': True
        }

        mock_list.return_value = ''
        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_getconfigvalue.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True,
            color='never'
        )
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_getconfigvalue.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(limit_to='sections')
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()


class TestStateExtensionExists(unittest.TestCase):

    @mock.patch('bin.commands.settings.list_')
    def test_state_extensionExists(self, mock_list):

        # given
        mock_list.return_value = '1'

        # when
        exists = state._extension_exists('log')

        # then
        mock_list.assert_called_once_with('git-state.extensions.log', count=True)
        self.assertTrue(exists)


class TestStateEditExtension(unittest.TestCase):

    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_editExtension_created(self, mock_info, mock_call, mock_extension_exists):

        # given
        mock_extension_exists.return_value = False

        # when
        state.edit_extension('log', command='git log', name='the log', options='-10', show=True, color=False)

        # then
        mock_extension_exists.assert_called_once_with('log')
        mock_call.assert_has_calls([
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.command', 'git log']),
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.name', 'the log']),
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.options', '-10']),
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.show', 'True']),
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.color', 'False'])
        ])
        mock_info.assert_called_once_with('Extension log created')

    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_editExtension_edited(self, mock_info, mock_call, mock_extension_exists):

        # given
        mock_extension_exists.return_value = True

        # when
        state.edit_extension('log', command='git log', name='the log', options='-10', show=True, color=False)

        # then
        mock_extension_exists.assert_called_once_with('log')
        mock_call.assert_has_calls([
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.command', 'git log']),
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.name', 'the log']),
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.options', '-10']),
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.show', 'True']),
            mock.call(['git', 'config', '--local', 'git-state.extensions.log.color', 'False'])
        ])
        mock_info.assert_called_once_with('Extension log updated')

    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_editExtension_onlyCommand(self, mock_info, mock_call, mock_extension_exists):

        # given
        mock_extension_exists.return_value = True

        # when
        state.edit_extension('log', command='git log', color=None)

        # then
        mock_extension_exists.assert_called_once_with('log')
        mock_call.assert_called_once_with(['git', 'config', '--local', 'git-state.extensions.log.command', 'git log'])
        mock_info.assert_called_once_with('Extension log updated')

    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_editExtension_onlyName(self, mock_info, mock_call, mock_extension_exists):

        # given
        mock_extension_exists.return_value = True

        # when
        state.edit_extension('log', name='the log', color=None)

        # then
        mock_extension_exists.assert_called_once_with('log')
        mock_call.assert_called_once_with(['git', 'config', '--local', 'git-state.extensions.log.name', 'the log'])
        mock_info.assert_called_once_with('Extension log updated')

    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_editExtension_onlyOptions(self, mock_info, mock_call, mock_extension_exists):

        # given
        mock_extension_exists.return_value = True

        # when
        state.edit_extension('log', options='-10', color=None)

        # then
        mock_extension_exists.assert_called_once_with('log')
        mock_call.assert_called_once_with(['git', 'config', '--local', 'git-state.extensions.log.options', '-10'])
        mock_info.assert_called_once_with('Extension log updated')

    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_editExtension_onlyShow(self, mock_info, mock_call, mock_extension_exists):

        # given
        mock_extension_exists.return_value = True

        # when
        state.edit_extension('log', show=False, color=None)

        # then
        mock_extension_exists.assert_called_once_with('log')
        mock_call.assert_called_once_with(['git', 'config', '--local', 'git-state.extensions.log.show', 'False'])
        mock_info.assert_called_once_with('Extension log updated')

    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_editExtension_onlyColor(self, mock_info, mock_call, mock_extension_exists):

        # given
        mock_extension_exists.return_value = True

        # when
        state.edit_extension('log', color=True)

        # then
        mock_extension_exists.assert_called_once_with('log')
        mock_call.assert_called_once_with(['git', 'config', '--local', 'git-state.extensions.log.color', 'True'])
        mock_info.assert_called_once_with('Extension log updated')


class TestStateGetExtensions(unittest.TestCase):

    @mock.patch('bin.commands.settings.list_')
    def test_state_getExtensions(self, mock_list):

        # given
        mock_list.return_value = '''git-state.extensions.log
git-state.extensions.changes'''

        # when
        extensions = state.get_extensions()

        # then
        mock_list.assert_called_once_with(limit_to='sections')

        self.assertEqual(extensions, ['log', 'changes'])

    @mock.patch('bin.commands.settings.list_')
    def test_state_getExtensions_noExtensionsExist(self, mock_list):

        # given
        mock_list.return_value = ''

        # when
        extensions = state.get_extensions()

        # then
        mock_list.assert_called_once_with(limit_to='sections')

        self.assertEqual(extensions, [])


class TestStatePrintExtensions(unittest.TestCase):

    @mock.patch('bin.commands.state.get_extensions')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_printExtensions(self, mock_info, mock_get_extensions):

        # given
        mock_get_extensions.return_value = ['log', 'changes', 'stashes']

        # when
        state.print_extensions()

        # then
        mock_get_extensions.assert_called_once()
        mock_info.assert_called_once_with('''changes
log
stashes''')

    @mock.patch('bin.commands.state.get_extensions')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_printExtensions_noExtensionsExist(self, mock_info, mock_get_extensions):

        # given
        mock_get_extensions.return_value = []

        # when
        state.print_extensions()

        # then
        mock_get_extensions.assert_called_once()
        mock_info.assert_not_called()


class TestStatePrintExtensionConfig(unittest.TestCase):

    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_printExtensionConfig(self, mock_info, mock_list):

        # given
        mock_list.return_value = 'config'

        # when
        state.print_extension_config('log')

        # then
        mock_list.assert_called_once_with(section='git-state.extensions.log', format_='pretty')
        mock_info.assert_called_once_with('config')

    @mock.patch('bin.commands.settings.list_')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_printExtensionConfig_extensionDoesNotExist(self, mock_info, mock_list):

        # given
        mock_list.return_value = ''

        # when
        state.print_extension_config('log')

        # then
        mock_list.assert_called_once_with(section='git-state.extensions.log', format_='pretty')
        mock_info.assert_not_called()


class TestStateRunExtension(unittest.TestCase):

    @mock.patch('colorama.init')
    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.state._run_extension')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.state._print_sections')
    def test_state_runExtension(self, mock_print_sections, mock_print_section, mock_run_extension, mock_extension_exists, mock_init):

        # given
        mock_extension_exists.return_value = True
        log_name = 'the log'
        log_text = 'log text'
        mock_run_extension.return_value = (log_name, log_text)
        section_text = 'section text'
        mock_print_section.return_value = section_text

        # when
        state.run_extension('log')

        # then
        mock_init.assert_called_once_with(strip=True)
        mock_extension_exists.assert_called_once_with('log')
        mock_run_extension.assert_called_once_with('log', {}, 'never')
        mock_print_section.assert_called_once_with(log_name, text=log_text, show_empty=True, color='never')
        mock_print_sections.assert_called_once_with({log_name: section_text})

    @mock.patch('colorama.init')
    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.state._run_extension')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.state._print_sections')
    def test_state_runExtension_extensionDoesNotExist(self, mock_print_sections, mock_print_section, mock_run_extension, mock_extension_exists, mock_init):

        # given
        mock_extension_exists.return_value = False

        # when
        state.run_extension('log')

        # then
        mock_init.assert_called_once_with(strip=True)
        mock_extension_exists.assert_called_once_with('log')
        mock_run_extension.assert_not_called()
        mock_print_section.assert_not_called()
        mock_print_sections.assert_not_called()


class TestStateDeleteExtension(unittest.TestCase):

    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_deleteExtension(self, mock_info, mock_call, mock_extension_exists):

        # given
        mock_extension_exists.return_value = True

        # when
        state.delete_extension('log')

        # then
        mock_extension_exists.assert_called_once_with('log')
        mock_call.assert_called_once_with('git config --local --remove-section git-state.extensions.log'.split())
        mock_info.assert_called_once_with('Extension log deleted')

    @mock.patch('bin.commands.state._extension_exists')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_deleteExtension_extensionDoesNotExist(elf, mock_info, mock_call, mock_extension_exists):

        # given
        mock_extension_exists.return_value = False

        # when
        state.delete_extension('log')

        # then
        mock_extension_exists.assert_called_once_with('log')
        mock_call.assert_not_called()
        mock_info.assert_not_called()
