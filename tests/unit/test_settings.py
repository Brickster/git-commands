import mock
import os
import unittest

from . import testutils
from bin.commands import settings


class TestSettings(unittest.TestCase):

    @mock.patch('bin.commands.utils.directories.is_git_repository')
    @mock.patch('bin.commands.utils.messages.error')
    def test__validateConfig_valid_notLocal(self, mock_error, mock_isgitrepository):

        # when
        settings._validate_config('global')

        # then
        mock_isgitrepository.assert_not_called()
        mock_error.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository')
    @mock.patch('bin.commands.utils.messages.error')
    def test__validateConfig_valid_localButIsGitRepository(self, mock_error, mock_isgitrepository):

        # given
        mock_isgitrepository.return_value = True

        # when
        settings._validate_config('local')

        # then
        mock_isgitrepository.assert_called_once()
        mock_error.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository')
    @mock.patch('bin.commands.utils.messages.error')
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test__validateConfig_invalid(self, mock_getcwd, mock_error, mock_isgitrepository):

        # given
        directory = '/cur/dir'
        mock_isgitrepository.return_value = False
        mock_getcwd.return_value = directory
        # mock_error.side_effect = [None, testutils.and_exit]

        # when
        try:
            settings._validate_config('local')
            # self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once()
        mock_error.assert_has_calls([
            mock.call('{0!r} is not a git repository'.format(directory), exit_=False),
            mock.call("'local' does not apply")
        ])
        mock_getcwd.assert_called_once()

    def test__prettyFormatConfigs(self):

        # given
        config_map = {
            'settings.keys.key1': 'value1',
            'settings.key3': 'value3',
            'settings.key2': 'value2',
            'a_setting.key0': 'value0'
        }

        # when
        formatted = settings._pretty_format_configs(config_map)

        # then: config if printed with keys sorted
        self.assertEqual(os.linesep.join(formatted), '''[a_setting]
    key0 = value0
[settings]
    key2 = value2
    key3 = value3
[settings "keys"]
    key1 = value1''')

    @mock.patch('bin.commands.utils.execute.stdout')
    @mock.patch('bin.commands.utils.messages.info')
    def test__dryDestroySection(self, mock_info, mock_stdout):

        # given
        config = 'local'
        section = 'section_name'
        keys = ('test.k1=v1', 'test.k2=v2')
        mock_stdout.return_value = os.linesep.join(keys) + os.linesep

        # when
        settings._dry_destroy_section(config, section)

        # then
        mock_stdout.assert_called_once_with(
            ('git', 'settings', 'list', '--format', 'compact', '--{}'.format(config), section)
        )
        mock_info.assert_has_calls([
            mock.call('Would be deleted from {}: {}'.format(config, keys[0])),
            mock.call('Would be deleted from {}: {}'.format(config, keys[1]))
        ])


class TestSettingsList(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._validate_config = settings._validate_config
        self._pretty_format_configs = settings._pretty_format_configs

    def tearDown(self):
        settings._validate_config = self._validate_config
        settings._pretty_format_configs = self._pretty_format_configs

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('bin.commands.utils.execute.check_output')
    def test_list(self, mock_checkoutput, mock_validateconfig):

        # given
        config_values = ['section.key1=value1', 'section.key2=value2']
        mock_checkoutput.return_value = '\x00'.join(config_values).replace('=', os.linesep) + '\x00'

        # when
        actual_values = settings.list_()

        # then
        self.assertEqual(sorted(actual_values.splitlines()), config_values)
        mock_validateconfig.assert_called_once()
        mock_checkoutput.assert_called_once_with(['git', 'config', '--list', '--null'])

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('bin.commands.utils.execute.check_output')
    def test_list_withOverrides(self, mock_checkoutput, mock_validateconfig):

        # given
        config_values = ['section.key1=override1', 'section.key2=value2']
        config_values_with_overrides = ['section.key1=value1'] + config_values
        mock_checkoutput.return_value = '\x00'.join(config_values_with_overrides).replace('=', os.linesep) + '\x00'

        # when
        actual_values = settings.list_()

        # then
        self.assertEqual(sorted(actual_values.splitlines()), config_values)
        mock_validateconfig.assert_called_once()
        mock_checkoutput.assert_called_once_with(['git', 'config', '--list', '--null'])

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('os.path.exists', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
    def test_list_withFile(self, mock_checkoutput, mock_exists, mock_validateconfig):

        # given
        file_path = '/file/path'
        config_values = ['section.key1=value1', 'section.key2=value2']
        mock_checkoutput.return_value = '\x00'.join(config_values).replace('=', os.linesep) + '\x00'

        # when
        actual_values = settings.list_(config='file', file_=file_path)

        # then
        self.assertEqual(sorted(actual_values.splitlines()), config_values)
        mock_validateconfig.assert_called_once()
        mock_exists.assert_called_once_with(file_path)
        mock_checkoutput.assert_called_once_with(['git', 'config', '--list', '--null', '--file', file_path])

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('os.path.exists', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_list_withFile_filesDoesNotExist(self, mock_error, mock_exists, mock_validateconfig):

        # given
        unknown_file = 'unknown_file'

        # when
        try:
            settings.list_(config='file', file_=unknown_file)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_validateconfig.assert_called_once()
        mock_error.assert_called_once_with('no such file {!r}'.format(unknown_file))

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('bin.commands.utils.execute.stdout')
    def test_list_withConfig(self, mock_stdout, mock_validateconfig):

        # given
        config_values = ['section.key1=value1', 'section.key2=value2']
        mock_stdout.return_value = '\x00'.join(config_values).replace('=', os.linesep) + '\x00'

        # when
        actual_values = settings.list_(config='global')

        # then
        self.assertEqual(sorted(actual_values.splitlines()), config_values)
        mock_validateconfig.assert_called_once()
        mock_stdout.assert_called_once_with(['git', 'config', '--list', '--null', '--global'])

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('bin.commands.utils.execute.stdout')
    def test_list_noConfigsFound(self, mock_stdout, mock_validateconfig):

        # given
        mock_stdout.return_value = ''

        # when
        actual_values = settings.list_(config='system')

        # then
        self.assertFalse(actual_values)
        mock_validateconfig.assert_called_once()
        mock_stdout.assert_called_once_with(['git', 'config', '--list', '--null', '--system'])

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('bin.commands.utils.execute.check_output')
    def test_list_withSection(self, mock_checkoutput, mock_validateconfig):

        # given
        config_values = ['section.key1=value1', 'section.key2=value2']
        mock_checkoutput.return_value = '\x00'.join(config_values + ['section2.k=v']).replace('=', os.linesep) + '\x00'

        # when
        actual_values = settings.list_(section='section')

        # then
        self.assertEqual(sorted(actual_values.splitlines()), config_values)
        mock_validateconfig.assert_called_once()
        mock_checkoutput.assert_called_once_with(['git', 'config', '--list', '--null'])

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('bin.commands.utils.execute.check_output')
    def test_list_count(self, mock_checkoutput, mock_validateconfig):

        # given
        config_values = ['section.key1=value1', 'section.key2=value2']
        mock_checkoutput.return_value = '\x00'.join(config_values).replace('=', os.linesep) + '\x00'

        # when
        actual_count = settings.list_(count=True)

        # then
        self.assertEqual(actual_count, '2')
        mock_validateconfig.assert_called_once()
        mock_checkoutput.assert_called_once_with(['git', 'config', '--list', '--null'])

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('bin.commands.utils.execute.check_output')
    def test_list_keysOnly(self, mock_checkoutput, mock_validateconfig):

        # given
        config_values = ['section.key1=value1', 'section.key2=value2']
        mock_checkoutput.return_value = '\x00'.join(config_values).replace('=', os.linesep) + '\x00'

        # when
        actual_values = settings.list_(limit_to='keys')

        # then
        self.assertEqual(sorted(actual_values.splitlines()), ['key1', 'key2'])
        mock_validateconfig.assert_called_once()
        mock_checkoutput.assert_called_once_with(['git', 'config', '--list', '--null'])

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('bin.commands.utils.execute.check_output')
    def test_list_sectionsOnly(self, mock_checkoutput, mock_validateconfig):

        # given
        config_values = ['section.key1=value1', 'section.key2=value2', 'section2.key1=value1']
        mock_checkoutput.return_value = '\x00'.join(config_values).replace('=', os.linesep) + '\x00'

        # when
        actual_values = settings.list_(limit_to='sections')

        # then
        self.assertEqual(sorted(actual_values.splitlines()), ['section', 'section2'])
        mock_validateconfig.assert_called_once()
        mock_checkoutput.assert_called_once_with(['git', 'config', '--list', '--null'])

    @mock.patch('bin.commands.settings._validate_config')
    @mock.patch('bin.commands.settings._pretty_format_configs')
    @mock.patch('bin.commands.utils.execute.check_output')
    def test_list_prettyFormat(self, mock_checkoutput, mock_prettyformatconfig, mock_validateconfig):

        # given
        config_values = ['section.keys.key1=value1', 'section.keys.key2=value2', 'sec.key=value']
        mock_checkoutput.return_value = '\x00'.join(config_values).replace('=', os.linesep) + '\x00'
        format_result = ['formatted results']
        mock_prettyformatconfig.return_value = format_result

        # when
        pretty_output = settings.list_(format_='pretty')

        # then
        self.assertEqual(pretty_output, format_result[0])
        mock_validateconfig.assert_called_once()
        mock_checkoutput.assert_called_once_with(['git', 'config', '--list', '--null'])


class TestSettingsDestroy(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._dry_destroy_section = settings._dry_destroy_section

    def tearDown(self):
        settings._dry_destroy_section = self._dry_destroy_section

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_destroy_hasLocal(self, mock_swallow, mock_isgitrepository):

        # given
        section = 'section_name'
        dry_run = False

        # when
        settings.destroy(section, dry_run)

        # then
        mock_isgitrepository.assert_called_once()
        mock_swallow.assert_has_calls([
            mock.call(('git', 'config', '--local', '--remove-section', section)),
            mock.call(('git', 'config', '--global', '--remove-section', section)),
            mock.call(('git', 'config', '--system', '--remove-section', section))
        ])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.execute.swallow')
    def test_destroy_noLocal(self, mock_swallow, mock_isgitrepository):

        # given
        section = 'section_name'
        dry_run = False

        # when
        settings.destroy(section, dry_run)

        # then
        mock_isgitrepository.assert_called_once()
        mock_swallow.assert_has_calls([
            mock.call(('git', 'config', '--global', '--remove-section', section)),
            mock.call(('git', 'config', '--system', '--remove-section', section))
        ])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.settings._dry_destroy_section')
    def test_destroy_dryRun_hasLocal(self, mock_drydestroysection, mock_isgitrepository):

        # given
        section = 'section_name'
        dry_run = True

        # when
        settings.destroy(section, dry_run)

        # then
        mock_isgitrepository.assert_called_once()
        mock_drydestroysection.assert_has_calls([
            mock.call('local', section),
            mock.call('global', section),
            mock.call('system', section)
        ])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.settings._dry_destroy_section')
    def test_destroy_dryRun_noLocal(self, mock_drydestroysection, mock_isgitrepository):

        # given
        section = 'section_name'
        dry_run = True

        # when
        settings.destroy(section, dry_run)

        # then
        mock_isgitrepository.assert_called_once()
        mock_drydestroysection.assert_has_calls([
            mock.call('global', section),
            mock.call('system', section)
        ])
