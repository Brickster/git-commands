import os
import shutil
import subprocess
import tempfile
import unittest

import git


class TestState(unittest.TestCase):

    def setUp(self):
        # The current directory may not exist if this test ran after another functional test. So just create a new one.
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def _output(self, command):
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0]

    def test_state_version(self):

        # expect
        self.assertRegexpMatches(self._output('git state -v'), '^git-state \\d+\\.\\d+\\.\\d+$')
        self.assertRegexpMatches(self._output('git state --version'), '^git-state \\d+\\.\\d+\\.\\d+$')

    def test_state_help(self):

        # expect
        self.assertRegexpMatches(self._output('git state -h'), '^usage: git state')
        self.assertRegexpMatches(self._output('git state --help'), '^GIT-STATE\\(1\\)')


class TestStateNoExtension(unittest.TestCase):

    def _output(self, command):
        pyenv = os.environ.copy()
        pyenv['GIT_CONFIG'] = self.dirpath + '/.git/config'
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=pyenv)
        return proc.communicate()[0]

    def setUp(self):

        # init repo
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        self.repo.config_writer('repository').set_value('color', 'ui', 'never').release()

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test_state_cleanAndEmptyRepository(self):
        # expect
        self.assertEqual(self._output('git state'), '''# status (master)
nothing to commit, repository is empty
''')

    def test_state_workingDirectoryIsClean(self):

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

    def test_state_doNotShowStatusCleanMessage_whenRepositoryIsEmpty(self):

        # given
        self._output('git config git-state.status.show-clean-message False')

        # expect
        self.assertFalse(self._output('git state'))

    def test_state_doNotShowStatusCleanMessage_whenWorkingDirectoryIsClean(self):

        # given: an initial commit
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])
        self._output('git config git-state.status.show-clean-message False')

        # expect
        self.assertEqual(self._output('git state'), '# status (master)\n')

    def test_state_showStatus(self):

        # given
        self._output('git config git-state.status.show false')
        expected = '''# status (master)
nothing to commit, repository is empty
'''

        # expect
        self.assertEqual(self._output('git state --status'), expected)
        self.assertEqual(self._output('git state -s'), expected)

    def test_state_noShowStatus(self):

        # given
        self._output('git config git-state.status.show true')

        # expect
        self.assertFalse(self._output('git state --no-status'))
        self.assertFalse(self._output('git state -S'))


class TestStateWithExtension(unittest.TestCase):

    def _output(self, command):
        pyenv = os.environ.copy()
        pyenv['GIT_CONFIG'] = self.dirpath + '/.git/config'
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=pyenv)
        return proc.communicate()[0]

    def setUp(self):

        # init repo
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        self.repo.config_writer('repository').set_value('color', 'ui', 'never').release()
        self.repo.config_writer('repository').set_value('git-state.extensions', 'log', 'git log --oneline').release()

        # initial commit
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())
        pyenv = os.environ.copy()
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-15T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-15T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'], env=pyenv)
        self.commit0_log = subprocess.check_output('git rev-parse --short HEAD'.split()).strip() + ' Initial commit'

        # edit readme
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-16T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-16T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-a', '-m', 'edit readme'], env=pyenv)
        self.commit1_log = subprocess.check_output('git rev-parse --short HEAD'.split()).strip() + ' edit readme'

        # add changelog
        subprocess.call('touch CHANGELOG.md'.split())
        subprocess.call('git add -A'.split())
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-17T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-17T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'add changelog'], env=pyenv)
        self.commit2_log = subprocess.check_output('git rev-parse --short HEAD'.split()).strip() + ' add changelog'

        # edit changelog
        with open('CHANGELOG.md', 'w') as a_file:
            a_file.write('changelog\n')
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-18T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-18T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-a', '-m', 'edit changelog'], env=pyenv)
        self.commit3_log = subprocess.check_output('git rev-parse --short HEAD'.split()).strip() + ' edit changelog'

        self.full_log = os.linesep.join([self.commit3_log, self.commit2_log, self.commit1_log, self.commit0_log])

    def test_state_withExtension(self):

        # expect
        self.assertEqual(self._output('git state'), '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log))

    def test_state_withExtension_order(self):

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

    def test_state_withExtension_orderConfig(self):

        # given
        self._output('git config git-state.order log status')

        # expect
        self.assertEqual(self._output('git state'), '''# log
{}
# status (master)
nothing to commit, working directory is clean
'''.format(self.full_log))

    def test_state_withExtension_orderConfig_overriddenWithFlag(self):

        # given
        self._output('git config git-state.order log status')

        # expect
        self.assertEqual(self._output('git state --order status log'), '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log))

    def test_state_withExtension_options(self):

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

    def test_state_withExtension_optionsConfig(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'options', '-2')
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
{}
'''.format(self.commit3_log, self.commit2_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_withExtension_nameConfig(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'name', 'git log')
        expected = '''# status (master)
nothing to commit, working directory is clean
# git log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_withExtension_showExtensionUsingFlag(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state --show-log'), expected)

    def test_state_withExtension_noShowExtensionUsingFlag(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'true').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
'''

        # expect
        self.assertEqual(self._output('git state --no-show log'), expected)
        self.assertEqual(self._output('git state --no-show-log'), expected)

    def test_state_withExtension_showExtensionUsingConfig(self):

        # given
        self._output('git config git-state.extensions.log.show true')
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_withExtension_noShowExtensionUsingConfig(self):

        # given
        self._output('git config git-state.extensions.log.show false')
        expected = '''# status (master)
nothing to commit, working directory is clean
'''

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_withExtension_noShowEmptyIsDefault(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions', 'stashes', 'git stash list').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_withExtension_showEmptyUsingFlag(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        self.repo.config_writer('repository').set_value('git-state.extensions', 'stashes', 'git stash list').release()
        self.repo.config_writer('repository').set_value('git-state', 'show-empty', 'false').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# stashes
'''

        # expect
        self.assertEqual(self._output('git state --show-empty'), expected)
        self.assertEqual(self._output('git state -e'), expected)

    def test_state_withExtension_noShowEmptyUsingFlag(self):

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

    def test_state_withExtension_showEmptyUsingConfig(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        self.repo.config_writer('repository').set_value('git-state.extensions', 'stashes', 'git stash list').release()
        self.repo.config_writer('repository').set_value('git-state', 'show-empty', 'true').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
# stashes
'''

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_withExtension_noShowEmptyUsingConfig(self):

        # given
        self.repo.config_writer('repository').set_value('git-state.extensions.log', 'show', 'false').release()
        self.repo.config_writer('repository').set_value('git-state.extensions', 'stashes', 'git stash list').release()
        self.repo.config_writer('repository').set_value('git-state', 'show-empty', 'false').release()
        expected = '''# status (master)
nothing to commit, working directory is clean
'''

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_withExtension_noShowAll(self):

        # expect
        self.assertEqual(self._output('git state --no-show-all'), '''# status (master)
nothing to commit, working directory is clean
''')

    def test_state_withExtension_formatCompactIsDefault(self):

        # given
        expected = '''# status (master)
nothing to commit, working directory is clean
# log
{}
'''.format(self.full_log)

        # expect
        self.assertEqual(self._output('git state'), expected)

    def test_state_withExtension_formatCompact(self):

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

    def test_state_withExtension_formatPretty(self):

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
