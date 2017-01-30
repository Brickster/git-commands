import mock
import os
import subprocess
import unittest

import colorama

import testutils
from bin.commands import state


class TestStatePrintSection(unittest.TestCase):

    def test_printsection_withaccent(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        accent = 'the accent'
        expected_output = '# ' + colorama.Fore.GREEN + title + ' ' + accent + colorama.Fore.RESET + os.linesep + text

        # when
        section_output = state._print_section(title, accent=accent, text=text)

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_withoutaccent(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        expected_output = '# ' + colorama.Fore.GREEN + title + colorama.Fore.RESET + os.linesep + text

        # when
        section_output = state._print_section(title, accent=None, text=text)

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_donotshowempty_notext(self):

        # when
        section_output = state._print_section('title', text=None, show_empty=False)

        # then
        self.assertEqual(section_output, '')

    def test_printsection_donotshowempty_withtext(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        expected_output = '# ' + colorama.Fore.GREEN + title + colorama.Fore.RESET + os.linesep + text

        # when
        section_output = state._print_section(title, accent=None, text=text, show_empty=False)

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
        section_output = state._print_section(title, text=text, format_='pretty')

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_prettyandnotext(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        expected_output = "# {}{}{}".format(colorama.Fore.GREEN, title, colorama.Fore.RESET) + os.linesep + os.linesep

        # when
        section_output = state._print_section(title, text=None, format_='pretty', show_empty=True)

        # then
        self.assertEqual(section_output, expected_output)

    def test_printsection_compact(self):

        # setup
        text = 'the text\nhere\n'
        title = 'the title'
        expected_output = '# ' + colorama.Fore.GREEN + title + colorama.Fore.RESET + os.linesep + text

        # when
        section_output = state._print_section(title, text=text)

        # then
        self.assertEqual(section_output, expected_output)

    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_printsection_unknownformat(self, mock_error):

        # when
        try:
            state._print_section('title', text='text', format_='invalid')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_error.assert_called_once_with("unknown format 'invalid'")


class TestStateState(unittest.TestCase):

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
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
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': []
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_get.side_effect = [True, []]

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
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_alloff(
            self,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': False,
            'clear': False,
            'ignore_extensions': []
        }

        mock_get.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_not_called()
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('')
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
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
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
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': []
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_get.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_statusget.assert_called_once_with(
            clear=False,
            format='compact',
            ignore_extensions=[],
            show_clean_message=True,
            show_color='never',
            show_status=True
        )
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('sys.stdout.isatty', return_value=False)
    @mock.patch('colorama.init')
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_showcolor_autoandnotatty(
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
            mock_init,
            mock_isatty,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'auto',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': []
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_get.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isatty.assert_called_once_with()
        mock_init.assert_called_once_with(strip=True)
        mock_statusget.assert_called_once_with(
            clear=False,
            format='compact',
            ignore_extensions=[],
            show_clean_message=True,
            show_color='never',
            show_status=True
        )
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('sys.stdout.isatty', return_value=True)
    @mock.patch('colorama.init')
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_showcolor_autoandatty(
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
            mock_init,
            mock_isatty,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'auto',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': []
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_get.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isatty.assert_called_once_with()
        mock_init.assert_called_once_with()
        mock_statusget.assert_called_once_with(
            clear=False,
            format='compact',
            ignore_extensions=[],
            show_clean_message=True,
            show_color='always',
            show_status=True
        )
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_,
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=True)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_state_emptyrepository(
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
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        show_empty = True
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'clear': False,
            'ignore_extensions': [],
            'show_empty': show_empty
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'section output\n'
        mock_get.side_effect = [True, []]

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_called_once_with(
            mock_statustitle.return_value,
            mock_statusaccent.return_value,
            mock_statusget.return_value,
            format_
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_not_called()
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('section output')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_withextensions(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': False,
            'clear': False,
            'ignore_extensions': [],
            'options': {}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_get.side_effect = [True, True, changes_command, changes_name, [], True, []]
        mock_list.return_value = 'changes'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [changes_output, None]
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
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
            show_empty=None
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_popen.assert_called_once_with(
            ['changes', 'command', '--color=never'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        mock_proc.communicate.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_withextensions_doesNotSupportColor(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': False,
            'clear': False,
            'ignore_extensions': [],
            'options': {}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_get.side_effect = [True, True, changes_command, changes_name, [], False, []]
        mock_list.return_value = 'changes'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [changes_output, None]
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
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
            show_empty=None
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_popen.assert_called_once_with(
            ['changes', 'command'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        mock_proc.communicate.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_withextensions_withoptions_fromcommandline(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': False,
            'clear': False,
            'ignore_extensions': [],
            'options': {'changes': ['--option1', '-o "1 2"']}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_get.side_effect = [True, True, changes_command, changes_name, [], True, []]
        mock_list.return_value = 'changes'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [changes_output, None]
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
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
            show_empty=None
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_popen.assert_called_once_with(
            ['changes', 'command', '--option1', '-o', '1 2', '--color=never'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        mock_proc.communicate.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_withextensions_withoptions_fromconfig(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': False,
            'clear': False,
            'ignore_extensions': [],
            'options': {}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_get.side_effect = [True, True, changes_command, changes_name, ['--option1 -o "1 2"'], True, []]
        mock_list.return_value = 'changes'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [changes_output, None]
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
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
            show_empty=None
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_popen.assert_called_once_with(
            ['changes', 'command', '--option1', '-o', '1 2', '--color=never'], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mock_proc.communicate.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_withextensions_withoptions_fromcommandlineandconfig(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': False,
            'clear': False,
            'ignore_extensions': [],
            'options': {'changes': ['--option1', '-o "1 2"']}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_get.side_effect = [True, True, changes_command, changes_name, ['--option2 true'], True, []]
        mock_list.return_value = 'changes'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [changes_output, None]
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
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
            show_empty=None
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_popen.assert_called_once_with(
            ['changes', 'command', '--option2', 'true', '--option1', '-o', '1 2', '--color=never'], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mock_proc.communicate.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
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
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': False,
            'clear': False,
            'ignore_extensions': ['changes'],
            'options': {}
        }
        mock_get.side_effect = [True, []]
        mock_list.return_value = 'changes'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_not_called()
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('')
        mock_call.assert_not_called()
        mock_popen.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
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
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': False,
            'clear': False,
            'ignore_extensions': [],
            'options': {}
        }
        mock_get.side_effect = [True, False, []]
        mock_list.return_value = 'changes'

        # when
        state.state(**kwargs)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_printsection.assert_not_called()
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('')
        mock_call.assert_not_called()
        mock_popen.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_withextensions_ignoredViaConfig_showViaCommandLine(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_isemptyrepository,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': False,
            'clear': False,
            'ignore_extensions': [],
            'show_extensions': ['changes'],
            'options': {}
        }
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_get.side_effect = [True, changes_command, changes_name, [], True, []]
        mock_list.return_value = 'changes'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [changes_output, None]
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
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
            show_empty=None
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('final changes output')
        mock_call.assert_not_called()
        mock_popen.assert_called_once_with(
            ['changes', 'command', '--color=never'], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        mock_proc.communicate.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_withorder(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': [],
            'options': {}
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.side_effect = ['status section\n', 'changes section\n']
        changes_command = 'changes command'
        changes_name = 'changes'
        changes_output = 'the changes'
        mock_get.side_effect = [True, True, changes_command, changes_name, [], True, ['changes', 'status']]
        mock_list.return_value = 'changes'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [changes_output, None]
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

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
                show_empty=True
            ),
            mock.call(
                title=changes_name,
                text=changes_output,
                format_=format_,
                show_empty=None
            )
        ])
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes.show', default=True, as_type=mock.ANY),
            mock.call('git-state.extensions.changes'),
            mock.call('git-state.extensions.changes.name', default='changes'),
            mock.call('git-state.extensions.changes.options', default=[], as_type=mock.ANY),
            mock.call('git-state.extensions.changes.color', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('changes section\nstatus section')
        mock_call.assert_not_called()
        mock_popen.assert_called_once_with(
            ['changes', 'command', '--color=never'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mock_proc.communicate.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
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
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': []
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.side_effect = ['status section\n']
        mock_get.side_effect = [True, ['status', 'unknown']]

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
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='1')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('subprocess.Popen')
    def test_state_pageOutput(
            self,
            mock_popen,
            mock_info,
            mock_call,
            mock_checkoutput,
            mock_list,
            mock_printsection,
            mock_statusaccent,
            mock_statustitle,
            mock_statusget,
            mock_isemptyrepository,
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': []
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\ntwo\nthree\nfour\nfive\n'
        mock_get.side_effect = [True, []]
        mock_echo = mock.Mock()
        mock_echo.stdout = 'mock out'
        mock_popen.return_value = mock_echo

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
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_not_called()
        mock_call.assert_called_once_with(['less', '-r'], stdin=mock_echo.stdout)
        mock_popen.assert_called_once_with(['echo', 'status section\ntwo\nthree\nfour\nfive'], stdout=subprocess.PIPE)
        mock_echo.wait.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='1')
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
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': [],
            'page': False
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\ntwo\nthree\nfour\nfive\n'
        mock_get.side_effect = [True, []]

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
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section\ntwo\nthree\nfour\nfive')

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('colorama.init')
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
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
            mock_get,
            mock_init,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': [],
            'clear': True
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_get.side_effect = [True, []]

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
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_called_once_with('clear')

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
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
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': [],
            'clear': True
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_get.side_effect = [True, []]

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
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings.get', return_value=False)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.stateextensions.status.get')
    @mock.patch('bin.commands.stateextensions.status.title')
    @mock.patch('bin.commands.stateextensions.status.accent')
    @mock.patch('bin.commands.state._print_section')
    @mock.patch('bin.commands.settings.list_', return_return='')
    @mock.patch('subprocess.check_output', return_value='100')
    @mock.patch('subprocess.call')
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
            mock_get,
            mock_isgitrepository
    ):

        # setup
        format_ = 'compact'
        kwargs = {
            'show_color': 'never',
            'format': format_,
            'show_status': True,
            'clear': False,
            'ignore_extensions': [],
            'clear': False
        }

        mock_statusget.return_value = 'status output'
        mock_statustitle.return_value = 'status title'
        mock_statusaccent.return_value = 'status accent'
        mock_printsection.return_value = 'status section\n'
        mock_get.side_effect = [True, []]

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
            show_empty=True
        )
        mock_get.assert_has_calls([
            mock.call('git-state.status.show-clean-message', default=True, as_type=mock.ANY),
            mock.call('git-state.order', default=[], as_type=mock.ANY)
        ])
        self.assertEqual(mock_get.call_args_list[0][1]['as_type'].func_name, 'as_bool')
        mock_list.assert_called_once_with(
            section='git-state.extensions',
            config=None,
            count=False,
            keys=True,
            format=None,
            file=None
        )
        mock_checkoutput.assert_called_once_with('tput lines'.split())
        mock_info.assert_called_once_with('status section')
        mock_call.assert_not_called()
