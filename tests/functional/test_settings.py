import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import git

from . import testutils


class TestSettings(unittest.TestCase):

    def _output(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].decode('utf-8').strip()

    def test_settings_version(self):

        # expect
        self.assertRegexpMatches(self._output('git settings -v'.split()), 'git-settings \\d+\\.\\d+\\.\\d+')
        self.assertRegexpMatches(self._output('git settings --version'.split()), 'git-settings \\d+\\.\\d+\\.\\d+')

    def test_settings_help(self):

        # expect
        self.assertTrue(self._output('git settings -h'.split()))
        self.assertTrue(self._output('git settings --help'.split()))


class TestSettingsList(unittest.TestCase):

    def _output(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].decode('utf-8').strip()

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)

        # recreate the local config
        os.remove(self.dirpath + '/.git/config')
        open(self.dirpath + '/.git/config', 'w').close()

        # set some configs
        self.repo.git.config('--local', 'git-settings.test.geta', 'valuea')
        self.repo.git.config('--local', 'git-settings.test.getb', 'valueb')
        self.repo.git.config('--local', 'git-settings.test2.getc', 'valuec')

    def tearDown(self):
        # put global configs back since some tests remove them
        if '--config' in sys.argv or '-c' in sys.argv:
            self.repo.git.config('--global', 'user.name', 'Marcus Rosenow')
            self.repo.git.config('--global', 'user.email', 'Brickstertwo@users.noreply.github.com')
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_list(self):

        # when
        actual = self.repo.git.settings('list')

        # then
        self.assertTrue('git-settings.test.geta=valuea' in actual)
        self.assertTrue('git-settings.test.getb=valueb' in actual)
        self.assertTrue('git-settings.test2.getc=valuec' in actual)

    def test_list_section(self):

        # when
        configs_list = self.repo.git.settings('list', 'git-settings.test').splitlines()

        # then
        self.assertEqual(len(configs_list), 2)
        self.assertTrue('git-settings.test.geta=valuea' in configs_list)
        self.assertTrue('git-settings.test.getb=valueb' in configs_list)

    def test_list_local(self):

        # when
        actual = self.repo.git.settings('list', '--local')

        # then
        self.assertEqual(len(actual.splitlines()), 3)
        self.assertTrue('git-settings.test.geta=valuea' in actual)
        self.assertTrue('git-settings.test.getb=valueb' in actual)
        self.assertTrue('git-settings.test2.getc=valuec' in actual)

    def test_list_local_configFileDoesNotExist(self):

        # given: no local config
        os.remove(self.dirpath + '/.git/config')

        # when
        stdout = self._output('git settings list --local'.split())

        # then
        self.assertFalse(stdout)

    @unittest.skipIf(
        '--config' not in sys.argv and '-c' not in sys.argv,
        'requires editing user config and should only run during non-local builds.'
    )
    def test_list_global(self):

        # given
        self.repo.git.config('--global', 'git-settings.test_global.get', 'value')

        # when
        actual = self.repo.git.settings('list', '--global')

        # then
        self.assertTrue('git-settings.test_global.get=value' in actual)
        self.assertTrue('git-settings.test.geta=valuea' not in actual)

        # cleanup
        self.repo.git.config('--global', '--remove-section', 'git-settings.test_global')

    # too dangerous to edit the user's configs for anything more complicated
    def test_list_global_safe(self):

        # when
        actual = self.repo.git.settings('list', '--global')

        # then
        self.assertTrue('git-settings.test.geta=valuea' not in actual)
        self.assertTrue('git-settings.test.getb=valueb' not in actual)
        self.assertTrue('git-settings.test2.getc=valuec' not in actual)

    @unittest.skipIf(
        '--config' not in sys.argv and '-c' not in sys.argv,
        'requires editing user config and should only run during non-local builds.'
    )
    def test_list_global_configFileDoesNotExist(self):

        # given: no global config
        if os.path.exists(os.path.expanduser('~/.gitconfig')):
            os.remove(os.path.expanduser('~/.gitconfig'))
        if os.path.exists(os.path.expanduser('~/.config/git/config')):
            os.remove(os.path.expanduser('~/.config/git/config'))

        # when
        stdout = self._output('git settings list --global'.split())

        # then
        self.assertFalse(stdout)

    # a bit of a hack since --no-skip is a nosetests flag.
    @unittest.skipIf(
        '--config' not in sys.argv and '-c' not in sys.argv,
        'requires editing user config and should only run during non-local builds.'
    )
    def test_list_system(self):

        # given
        self.repo.git.config('--system', 'git-settings.test_system.get', 'value')

        # when
        actual = self.repo.git.settings('list', '--system')

        # then
        self.assertTrue('git-settings.test_system.get=value' in actual)
        self.assertTrue('git-settings.test.geta=valuea' not in actual)

        # cleanup
        self.repo.git.config('--system', '--remove-section', 'git-settings.test_system')

    # too dangerous to edit the user's configs for anything more complicated
    def test_list_system_safe(self):

        # when
        actual = self.repo.git.settings('list', '--system')

        # then
        self.assertTrue('git-settings.test.geta=valuea' not in actual)
        self.assertTrue('git-settings.test.getb=valueb' not in actual)
        self.assertTrue('git-settings.test2.getc=valuec' not in actual)

    @unittest.skipIf(
        '--config' not in sys.argv and '-c' not in sys.argv,
        'requires editing user config and should only run during non-local builds.'
    )
    def test_list_system_configFileDoesNotExist(self):

        # given: no system config
        if os.path.exists('/etc/gitconfig'):
            os.remove('/etc/gitconfig')
        if os.path.exists('/usr/local/etc/gitconfig'):
            os.remove('/usr/local/etc/gitconfig')

        # when
        stdout = self._output('git settings list --system'.split())

        # then
        self.assertFalse(stdout)

    def test_list_file(self):

        # given: a config file
        config_file = self.dirpath + '/config_file'
        shutil.copyfile(self.dirpath + '/.git/config', config_file)

        # given
        actual = self.repo.git.settings('list', '--file', config_file)

        # then
        self.assertEqual(len(actual.splitlines()), 3)
        self.assertTrue('git-settings.test.geta=valuea' in actual)
        self.assertTrue('git-settings.test.getb=valueb' in actual)
        self.assertTrue('git-settings.test2.getc=valuec' in actual)

    def test_list_format_compact(self):

        # when
        compact_settings = self.repo.git.settings('list', '--local', '--format=compact')

        # then
        self.assertEqual(compact_settings, """git-settings.test.geta=valuea
git-settings.test.getb=valueb
git-settings.test2.getc=valuec""")

    def test_list_format_pretty(self):

        # when
        pretty_settings = self.repo.git.settings('list', '--local', '--format=pretty')

        # then
        self.assertEqual(pretty_settings, """[git-settings "test"]
    geta = valuea
    getb = valueb
[git-settings "test2"]
    getc = valuec""")

    def test_list_pretty(self):

        # when
        pretty_settings = self.repo.git.settings('list', '--local', '--pretty')

        # then
        self.assertEqual(pretty_settings, """[git-settings "test"]
    geta = valuea
    getb = valueb
[git-settings "test2"]
    getc = valuec""")

    def test_list_count(self):
        self.assertEqual(int(self.repo.git.settings('list', '--local', '--count')), 3)

    def test_list_keys(self):

        # when
        keys = self.repo.git.settings('list', '--local', '--keys', 'git-settings.test').splitlines()

        # then
        self.assertEqual(keys, ['geta', 'getb'])

    def test_list_sections(self):

        # when
        sections = self.repo.git.settings('list', '--local', '--sections').splitlines()

        # then
        self.assertEqual(sorted(sections), ['git-settings.test', 'git-settings.test2'])

    def test_test_keysOptionRequiresASection(self):

        # run
        p = subprocess.Popen('git settings list --keys'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = [x.decode('utf-8') for x in p.communicate()]

        # verify
        self.assertFalse(stdout)
        self.assertEqual('error: argument -k/--keys: not allowed without positional argument section', stderr.strip())


@unittest.skipIf(
    '--config' not in sys.argv and '-c' not in sys.argv,
    'requires editing user config and should only run during non-local builds.'
)
class TestSettingsDestroy(unittest.TestCase):

    def _output(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].decode('utf-8').strip()

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)

        # recreate the local config
        os.remove(self.dirpath + '/.git/config')
        open(self.dirpath + '/.git/config', 'w').close()

        # setup config values
        self.repo.git.config('--local', 'git-settings.test.key', 'value')
        self.repo.git.config('--global', 'git-settings.test.key', 'value')
        self.repo.git.config('--system', 'git-settings.test.key', 'value')

    def tearDown(self):

        # just in case, clean up config values (use subprocess to suppress errors)
        with open(os.devnull, 'w') as devnull:
            subprocess.call(('git', 'config', '--local', '--remove-section', 'git-settings.test'), stdout=devnull, stderr=devnull)
            subprocess.call(('git', 'config', '--global', '--remove-section', 'git-settings.test'), stdout=devnull, stderr=devnull)
            subprocess.call(('git', 'config', '--system', '--remove-section', 'git-settings.test'), stdout=devnull, stderr=devnull)

        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_destory(self):

        # when
        destroy_output = self.repo.git.settings('destroy', 'git-settings.test')

        # then
        self.assertFalse(destroy_output, 'destroy should have no output')
        self.assertFalse(self._output('git config --get-regexp git-settings.test'.split()))

    def test_destory_localOnly(self):

        # given
        self.repo.git.config('--system', '--remove-section', 'git-settings.test')
        self.repo.git.config('--global', '--remove-section', 'git-settings.test')

        # when
        destroy_output = self.repo.git.settings('destroy', 'git-settings.test')

        # then
        self.assertFalse(destroy_output, 'destroy should have no output')
        self.assertFalse(self._output('git config --get-regexp git-settings.test'.split()))

    def test_destory_globalOnly(self):

        # given
        self.repo.git.config('--local', '--remove-section', 'git-settings.test')
        self.repo.git.config('--system', '--remove-section', 'git-settings.test')

        # when
        destroy_output = self.repo.git.settings('destroy', 'git-settings.test')

        # then
        self.assertFalse(destroy_output, 'destroy should have no output')
        self.assertFalse(self._output('git config --get-regexp git-settings.test'.split()))

    def test_destory_systemOnly(self):

        # given
        self.repo.git.config('--local', '--remove-section', 'git-settings.test')
        self.repo.git.config('--global', '--remove-section', 'git-settings.test')

        # when
        destroy_output = self.repo.git.settings('destroy', 'git-settings.test')

        # then
        self.assertFalse(destroy_output, 'destroy should have no output')
        self.assertFalse(self._output('git config --get-regexp git-settings.test'.split()))

    def test_destory_dryRun(self):

        # when
        dry_destroy_output = self.repo.git.settings('destroy', '--dry-run', 'git-settings.test')

        # then
        self.assertEqual(dry_destroy_output, """Would be deleted from local: git-settings.test.key=value
Would be deleted from global: git-settings.test.key=value
Would be deleted from system: git-settings.test.key=value""")

    def test_destory_dryRun_localOnly(self):

        # given
        self.repo.git.config('--system', '--remove-section', 'git-settings.test')
        self.repo.git.config('--global', '--remove-section', 'git-settings.test')

        # when
        dry_destroy_output = self.repo.git.settings('destroy', '--dry-run', 'git-settings.test')

        # then
        self.assertEqual(dry_destroy_output, "Would be deleted from local: git-settings.test.key=value")

    def test_destory_dryRun_globalOnly(self):

        # given
        self.repo.git.config('--local', '--remove-section', 'git-settings.test')
        self.repo.git.config('--system', '--remove-section', 'git-settings.test')

        # when
        dry_destroy_output = self.repo.git.settings('destroy', '--dry-run', 'git-settings.test')

        # then
        self.assertEqual(dry_destroy_output, "Would be deleted from global: git-settings.test.key=value")

    def test_destory_dryRun_systemOnly(self):

        # given
        self.repo.git.config('--local', '--remove-section', 'git-settings.test')
        self.repo.git.config('--global', '--remove-section', 'git-settings.test')

        # when
        dry_destroy_output = self.repo.git.settings('destroy', '--dry-run', 'git-settings.test')

        # then
        self.assertEqual(dry_destroy_output, "Would be deleted from system: git-settings.test.key=value")
