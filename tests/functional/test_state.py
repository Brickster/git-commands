import os
import shutil
import subprocess
import tempfile
import unittest

import git

from . import testutils


class TestState(unittest.TestCase):

    def setUp(self):
        self.proj_dir = os.getcwd()
        # The current directory may not exist if this test ran after another functional test. So just create a new one.
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def _output(self, command):
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].decode('utf-8')

    def test_state_version(self):

        # expect
        self.assertRegexpMatches(self._output('git state -v'), '^git-state \\d+\\.\\d+\\.\\d+$')
        self.assertRegexpMatches(self._output('git state --version'), '^git-state \\d+\\.\\d+\\.\\d+$')

    def test_state_help(self):

        # expect
        self.assertRegexpMatches(self._output('git state -h'), '^usage: git state')
        self.assertRegexpMatches(self._output('git state --help'), 'GIT-STATE\\(1\\)')


class TestStateView(unittest.TestCase):

    def _output(self, command):
        pyenv = os.environ.copy()
        pyenv['GIT_CONFIG'] = self.dirpath + '/.git/config'
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=pyenv)
        return proc.communicate()[0].decode('utf-8')

    def setUp(self):
        self.proj_dir = os.getcwd()

        # init repo
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_state_view_cleanAndEmptyRepository(self):
        # expect
        self.assertEqual(self._output('git state'), '''# status (master)
nothing to commit, repository is empty
''')

    def test_state_view_workingDirectoryIsClean(self):

        # given: an initial commit
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])

        # expect
        self.assertEqual(self._output('git state'), '''# status (master)
nothing to commit, working directory is clean
''')

    def test_state_view_doNotShowStatusCleanMessage_whenRepositoryIsEmpty(self):

        # given
        self._output('git config git-state.status.show-clean-message False')

        # expect
        self.assertFalse(self._output('git state'))

    def test_state_view_doNotShowStatusCleanMessage_whenRepositoryIsEmpty_withFlagToShowEmpty(self):

        # given
        self._output('git config git-state.status.show-clean-message False')
        expected = '''# status (master)
'''

        # expect
        self.assertEqual(self._output('git state --show-empty'), expected)
        self.assertEqual(self._output('git state -e'), expected)

    def test_state_view_doNotShowStatusCleanMessage_whenRepositoryIsEmpty_withConfigToShowEmpty(self):
        # given
        self._output('git config git-state.status.show-clean-message false')
        self._output('git config git-state.show-empty true')
        expected = '''# status (master)
'''

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_view_doNotShowStatusCleanMessage_whenWorkingDirectoryIsClean(self):

        # given: an initial commit
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])
        self._output('git config git-state.status.show-clean-message False')

        # expect
        self.assertFalse(self._output('git state'))

    def test_state_view_doNotShowStatusCleanMessage_whenWorkingDirectoryIsClean_withFlagToNotShowEmpty(self):

        # given: an initial commit
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])
        self._output('git config git-state.status.show-clean-message false')
        self._output('git config git-state.show-empty true')

        # expect
        self.assertFalse(self._output('git state --no-show-empty'))
        self.assertFalse(self._output('git state -E'))

    def test_state_view_doNotShowStatusCleanMessage_whenWorkingDirectoryIsClean_withConfigToNotShowEmpty(self):

        # given: an initial commit
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])
        self._output('git config git-state.status.show-clean-message false')
        self._output('git config git-state.show-empty false')

        # expect
        self.assertFalse(self._output('git state'))


class TestStateViewWithExtension(unittest.TestCase):

    def _output(self, command):
        if type(command) == str:
            command = command.split()
        pyenv = os.environ.copy()
        pyenv['GIT_CONFIG'] = self.dirpath + '/.git/config'
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=pyenv)
        return proc.communicate()[0].decode('utf-8')

    def setUp(self):
        self.proj_dir = os.getcwd()

        # init repo
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'command', 'git log --oneline').release()

        # initial commit
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())
        pyenv = os.environ.copy()
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-15T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-15T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'], env=pyenv)
        self.commit0_log = subprocess.check_output('git rev-parse --short HEAD'.split()).decode('utf-8').strip() + ' Initial commit'

        # edit readme
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-16T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-16T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-a', '-m', 'edit readme'], env=pyenv)
        self.commit1_log = subprocess.check_output('git rev-parse --short HEAD'.split()).decode('utf-8').strip() + ' edit readme'

        # add changelog
        subprocess.call('touch CHANGELOG.md'.split())
        subprocess.call('git add -A'.split())
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-17T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-17T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'add changelog'], env=pyenv)
        self.commit2_log = subprocess.check_output('git rev-parse --short HEAD'.split()).decode('utf-8').strip() + ' add changelog'

        # edit changelog
        with open('CHANGELOG.md', 'w') as a_file:
            a_file.write('changelog\n')
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-18T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-18T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-a', '-m', 'edit changelog'], env=pyenv)
        self.commit3_log = subprocess.check_output('git rev-parse --short HEAD'.split()).decode('utf-8').strip() + ' edit changelog'

        self.full_log = os.linesep.join([self.commit3_log, self.commit2_log, self.commit1_log, self.commit0_log])

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_state_viewWithExtension(self):

        # expect
        self.assertEqual(self._output('git state'), '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log))

    def test_state_viewWithExtension_order(self):

        # given
        expected = '''# log
{}
# status (master)
nothing to commit, working directory is clean
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state --order log status'), expected)
        self.assertEqual(self._output('git state -o log status'), expected)
        self.assertEqual(self._output('git state --order log'), expected)

    def test_state_viewWithExtension_orderConfig(self):

        # given
        self._output('git config git-state.order log status')

        # expect
        self.assertEqual(self._output('git state'), '''# log
{}
# status (master)
nothing to commit, working directory is clean
'''.format(self.full_log))

    def test_state_viewWithExtension_orderConfig_overriddenWithFlag(self):

        # given
        self._output('git config git-state.order log status')

        # expect
        self.assertEqual(self._output('git state --order status log'), '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log))

    def test_state_viewWithExtension_options(self):

        # given
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
{}
'''.format(self.commit3_log, self.commit2_log)

        # expect
        self.assertEqual(self._output('git state --options log:-2'), expected)
        self.assertEqual(self._output('git state -O log:-2'), expected)

    def test_state_viewWithExtension_optionsConfig(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'options', '-2').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
{}
'''.format(self.commit3_log, self.commit2_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_viewWithExtension_nameConfig(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'name', 'git log').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# git log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_viewWithExtension_showAllFlag(self):
        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output(['git', 'state', '--show-all']), expected)

        # expect: show takes precedence
        self.assertEqual(self._output(['git', 'state', '--show-all', '--no-show', 'log']), expected)
        self.assertEqual(self._output(['git', 'state', '--no-show', 'log', '--show-all']), expected)

    def test_state_viewWithExtension_showExtensionUsingFlag(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output(['git', 'state', '--show', 'log']), expected)
        self.assertEqual(self._output(['git', 'state', '-s', 'log']), expected)

        # expect: show takes precedence
        self.assertEqual(self._output(['git', 'state', '--show', 'log', '--no-show', 'log']), expected)
        self.assertEqual(self._output(['git', 'state', '--no-show', 'log', '--show', 'log']), expected)

    def test_state_viewWithExtension_noShowExtensionUsingFlag(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'true').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
'''

        # expect
        self.assertEqual(self._output(['git', 'state', '--no-show', 'log']), expected)
        self.assertEqual(self._output(['git', 'state', '-S', 'log']), expected)

    def test_state_viewWithExtension_noShowExtensionUsingFlag_worksOnStatus(self):
        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'true').release()
        expected = '''# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output(['git', 'state', '--no-show', 'status']), expected)

    def test_state_viewWithExtension_showExtensionUsingConfig(self):

        # given
        self._output('git config git-state.extensions.log.show true')
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_viewWithExtension_noShowExtensionUsingConfig(self):

        # given
        self._output('git config git-state.extensions.log.show false')
        expected = '''# status (master)
nothing to commit, working directory is clean
'''

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_viewWithExtension_noShowEmptyIsDefault(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions', 'stashes', 'git stash list').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_viewWithExtension_showEmptyUsingFlag(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        self.repo.config_writer('repository').set_value('git-state.extensions.stashes', 'command', 'git stash list').release()
        self.repo.config_writer('repository').set_value('git-state', 'show-empty', 'false').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# stashes
'''

        # expect
        self.assertEqual(self._output('git state --show-empty'), expected)
        self.assertEqual(self._output('git state -e'), expected)

    def test_state_viewWithExtension_noShowEmptyUsingFlag(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        self.repo.config_writer('repository').set_value('git-state.extensions', 'stashes', 'git stash list').release()
        self.repo.config_writer('repository').set_value('git-state', 'show-empty', 'true').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
'''

        # expect
        self.assertEqual(self._output('git state --no-show-empty'), expected)
        self.assertEqual(self._output('git state -E'), expected)

    def test_state_viewWithExtension_showEmptyUsingConfig(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        self.repo.config_writer('repository').set_value('git-state.extensions.stashes', 'command', 'git stash list').release()
        self.repo.config_writer('repository').set_value('git-state', 'show-empty', 'true').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# stashes
'''

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_viewWithExtension_noShowEmptyUsingConfig(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        self.repo.config_writer('repository').set_value('git-state.extensions.stashes', 'command', 'git stash list').release()
        self.repo.config_writer('repository').set_value('git-state', 'show-empty', 'false').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
'''

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_viewWithExtension_formatCompactIsDefault(self):

        # given
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_viewWithExtension_formatCompact(self):

        # given
        self._output('git config git-state.format pretty')
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state --format compact'), expected)
        self.assertEqual(self._output('git state -f compact'), expected)

    def test_state_viewWithExtension_formatPretty(self):

        # given
        self._output('git config git-state.format compact')
        expected = '''# status (master)

    nothing to commit, working directory is clean

# log

    {}
    {}
    {}
    {}

'''.format(self.commit3_log, self.commit2_log, self.commit1_log, self.commit0_log)

        # expect
        self.assertEqual(self._output('git state --format pretty'), expected)
        self.assertEqual(self._output('git state -f pretty'), expected)
        self.assertEqual(self._output('git state --pretty'), expected)
        self.assertEqual(self._output('git state -p'), expected)


class TestStateExtensions(unittest.TestCase):

    def _output(self, command, set_config=True):
        if type(command) == str:
            command = command.split()
        pyenv = os.environ.copy()
        if set_config:
            pyenv['GIT_CONFIG'] = self.dirpath + '/.git/config'
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=pyenv)
        return proc.communicate()[0].decode('utf-8')

    def setUp(self):
        self.proj_dir = os.getcwd()

        # init repo
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)

        # initial commit
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())
        pyenv = os.environ.copy()
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-15T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-15T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'], env=pyenv)
        self.commit0_log = subprocess.check_output('git rev-parse --short HEAD'.split()).decode('utf-8').strip() + ' Initial commit'

        # edit readme
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-16T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-16T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-a', '-m', 'edit readme'], env=pyenv)
        self.commit1_log = subprocess.check_output('git rev-parse --short HEAD'.split()).decode('utf-8').strip() + ' edit readme'

        # add changelog
        subprocess.call('touch CHANGELOG.md'.split())
        subprocess.call('git add -A'.split())
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-17T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-17T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'add changelog'], env=pyenv)
        self.commit2_log = subprocess.check_output('git rev-parse --short HEAD'.split()).decode('utf-8').strip() + ' add changelog'

        # edit changelog
        with open('CHANGELOG.md', 'w') as a_file:
            a_file.write('changelog\n')
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-18T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-18T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-a', '-m', 'edit changelog'], env=pyenv)
        self.commit3_log = subprocess.check_output('git rev-parse --short HEAD'.split()).decode('utf-8').strip() + ' edit changelog'

        self.full_log = os.linesep.join([self.commit3_log, self.commit2_log, self.commit1_log, self.commit0_log])

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_state_extensions_create(self):

        # when
        create_output = self._output(['git', 'state', 'extensions', 'create', 'testlog', '--command', 'git log --oneline', '--options', '-10', '--name', 'the log', '--no-show', '--no-color'], set_config=False)

        # then
        self.assertEqual('Extension testlog created', create_output.strip())
        extension_config = self._output('git settings list git-state.extensions.testlog')
        self.assertIn('git-state.extensions.testlog.command=git log --oneline', extension_config)
        self.assertIn('git-state.extensions.testlog.name=the log', extension_config)
        self.assertIn('git-state.extensions.testlog.options=-10', extension_config)
        self.assertIn('git-state.extensions.testlog.show=False', extension_config)
        self.assertIn('git-state.extensions.testlog.color=False', extension_config)

    def test_state_extensions_create_extensionAlreadyExists(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.testlog', 'command', 'git log').release()

        # when
        create_output = self._output(['git', 'state', 'extensions', 'create', 'testlog', '--command', 'git log --oneline', '--options', '-10', '--name', 'the log', '--no-show', '--no-color'], set_config=False)

        # then
        self.assertEqual('Extension testlog updated', create_output.strip())
        extension_config = self._output('git settings list git-state.extensions.testlog')
        self.assertIn('git-state.extensions.testlog.command=git log --oneline', extension_config)
        self.assertIn('git-state.extensions.testlog.name=the log', extension_config)
        self.assertIn('git-state.extensions.testlog.options=-10', extension_config)
        self.assertIn('git-state.extensions.testlog.show=False', extension_config)
        self.assertIn('git-state.extensions.testlog.color=False', extension_config)

    def test_state_extensions_edit(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.testlog', 'command', 'git log').release()

        # when
        create_output = self._output(['git', 'state', 'extensions', 'edit', 'testlog', '--command', 'git log --oneline', '--options', '-10', '--name', 'the log', '--no-show', '--no-color'], set_config=False)

        # then
        self.assertEqual('Extension testlog updated', create_output.strip())
        extension_config = self._output('git settings list git-state.extensions.testlog')
        self.assertIn('git-state.extensions.testlog.command=git log --oneline', extension_config)
        self.assertIn('git-state.extensions.testlog.name=the log', extension_config)
        self.assertIn('git-state.extensions.testlog.options=-10', extension_config)
        self.assertIn('git-state.extensions.testlog.show=False', extension_config)
        self.assertIn('git-state.extensions.testlog.color=False', extension_config)

    def test_state_extensions_edit_extensionDoesNotExist(self):

        # when
        create_output = self._output(['git', 'state', 'extensions', 'edit', 'testlog', '--command', 'git log --oneline', '--options', '-10', '--name', 'the log', '--no-show', '--no-color'], set_config=False)

        # then
        self.assertEqual('Extension testlog created', create_output.strip())
        extension_config = self._output('git settings list git-state.extensions.testlog')
        self.assertIn('git-state.extensions.testlog.command=git log --oneline', extension_config)
        self.assertIn('git-state.extensions.testlog.name=the log', extension_config)
        self.assertIn('git-state.extensions.testlog.options=-10', extension_config)
        self.assertIn('git-state.extensions.testlog.show=False', extension_config)
        self.assertIn('git-state.extensions.testlog.color=False', extension_config)

    def test_state_extensions_delete(self):

        # given
        config_writer = self.repo.config_writer('repository')
        config_writer.set_value('git-state.extensions.log', 'color', 'True')
        config_writer.set_value('git-state.extensions.log', 'command', 'git log --oneline')
        config_writer.release()

        # expect
        self.assertEqual(self._output('git state extensions delete log', set_config=False).strip(), '''Extension log deleted''')
        self.assertFalse(self._output('git settings list git-state.extensions.log'))

    def test_state_extensions_delete_extensionDoesNotExist(self):
        # expect
        self.assertFalse(self._output('git state extensions delete blarg', set_config=False))

    def test_state_extensions_config(self):

        # given
        config_writer = self.repo.config_writer('repository')
        config_writer.set_value('git-state.extensions.log', 'color', 'True')
        config_writer.set_value('git-state.extensions.log', 'command', 'git log --oneline')
        config_writer.set_value('git-state.extensions.log', 'options', '-10')
        config_writer.set_value('git-state.extensions.log', 'show', 'false')
        config_writer.release()

        # expect
        self.assertEqual(self._output('git state extensions config log'), '''[git-state "extensions.log"]
    color = True
    command = git log --oneline
    options = -10
    show = false
''')

    def test_state_extensions_config_extensionDoesNotExist(self):
        # expect
        self.assertFalse(self._output('git state extensions config blarg'))

    def test_state_extensions_list(self):

        # given
        config_writer = self.repo.config_writer('repository')
        config_writer.set_value('git-state.extensions.log', 'command', 'git log --oneline')
        config_writer.set_value('git-state.extensions.changes', 'command', 'git changes')
        config_writer.release()

        # expect
        self.assertEqual(self._output('git state extensions list'), '''changes
log
''')

    def test_state_extensions_list_noneExist(self):
        # expect
        self.assertFalse(self._output('git state extensions list'))

    def test_state_extensions_run(self):

        # given
        config_writer = self.repo.config_writer('repository')
        config_writer.set_value('git-state.extensions.log', 'color', 'True')
        config_writer.set_value('git-state.extensions.log', 'command', 'git log --oneline')
        config_writer.set_value('git-state.extensions.log', 'options', '-10')
        config_writer.set_value('git-state.extensions.log', 'show', 'true')
        config_writer.release()

        # expect
        self.assertEqual(self._output('git state extensions run log'), '''# log
{}
'''.format(self.full_log))

    def test_state_extensions_run_extensionDoesNotExist(self):
        # expect
        self.assertFalse(self._output('git state extensions run blarg'))
