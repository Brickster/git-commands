import os
import shutil
import subprocess
import tempfile
import unittest

_DROPPED_FORMAT = 'Dropped refs/stash@{{{}}} ({})'
_DRY_RUN_FORMAT = 'Would drop refs/stash@{{{}}} ({})'
_STASH_FORMAT = '{} refs/stash@{{{}}}: WIP on master: {}'


class TestGitAbandon(unittest.TestCase):

    def _stashes(self):
        return subprocess.check_output(('git', 'stash', 'list', '--oneline', '--no-color'))

    def _output(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].strip()

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        subprocess.call('git init --quiet'.split())
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())

        # initial commit
        pyenv = os.environ.copy()
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-15T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-15T20:38:31Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'], env=pyenv)
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')
        self.initial_commit = subprocess.check_output('git log --no-color --oneline -1'.split()).strip()

        # stash@{3}
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-16T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-16T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())
        self.stash3 = subprocess.check_output('git rev-parse stash@{0}'.split()).strip()
        self.stash3_abbrev = subprocess.check_output('git rev-parse --short stash@{0}'.split()).strip()

        # stash@{2}
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-17T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-17T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())
        self.stash2 = subprocess.check_output('git rev-parse stash@{0}'.split()).strip()
        self.stash2_abbrev = subprocess.check_output('git rev-parse --short stash@{0}'.split()).strip()

        # stash@{1}
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-18T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-18T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())
        self.stash1 = subprocess.check_output('git rev-parse stash@{0}'.split()).strip()
        self.stash1_abbrev = subprocess.check_output('git rev-parse --short stash@{0}'.split()).strip()

        # stash@{0}
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-19T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-19T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())
        self.stash0 = subprocess.check_output('git rev-parse stash@{0}'.split()).strip()
        self.stash0_abbrev = subprocess.check_output('git rev-parse --short stash@{0}'.split()).strip()

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test_abandon_endOnly(self):

        # run
        abandon_output = subprocess.check_output('git abandon 2'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('0', self.stash0))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('1', self.stash1))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash2_abbrev, '0', self.initial_commit))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash3_abbrev, '1', self.initial_commit))

    def test_abandon_endOnly_negative(self):

        # test
        stdout, stderr = subprocess.Popen(
            'git abandon -10'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

        # verify
        self.assertFalse(stdout)
        self.assertEqual(stderr.strip(), 'error: end cannot be negative')

    def test_abandon_endOnly_pastEnd(self):

        # run
        abandon_output = subprocess.check_output('git abandon 10'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('0', self.stash0))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('1', self.stash1))
        self.assertEqual(abandon_output[2], _DROPPED_FORMAT.format('2', self.stash2))
        self.assertEqual(abandon_output[3], _DROPPED_FORMAT.format('3', self.stash3))
        self.assertFalse(self._stashes())

    def test_abandon_startAndEnd_all(self):

        # run
        abandon_output = subprocess.check_output('git abandon 0 4'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('0', self.stash0))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('1', self.stash1))
        self.assertEqual(abandon_output[2], _DROPPED_FORMAT.format('2', self.stash2))
        self.assertEqual(abandon_output[3], _DROPPED_FORMAT.format('3', self.stash3))
        self.assertFalse(self._stashes())

    def test_abandon_startAndEnd_fromZero(self):

        # run
        abandon_output = subprocess.check_output('git abandon 0 2'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('0', self.stash0))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('1', self.stash1))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash2_abbrev, '0', self.initial_commit))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash3_abbrev, '1', self.initial_commit))

    def test_abandon_startAndEnd_endsAtStashCount(self):

        # run
        abandon_output = subprocess.check_output('git abandon 2 4'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('2', self.stash2))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('3', self.stash3))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash0_abbrev, '0', self.initial_commit))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash1_abbrev, '1', self.initial_commit))

    def test_abandon_startAndEnd_pastEnd(self):

        # run
        abandon_output = subprocess.check_output('git abandon 2 10'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('2', self.stash2))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('3', self.stash3))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash0_abbrev, '0', self.initial_commit))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash1_abbrev, '1', self.initial_commit))

    def test_abandon_startAndEnd_startGreaterThanTotal(self):

        # test
        stdout, stderr = subprocess.Popen(
            'git abandon 100 200'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

        # verify
        self.assertFalse(stdout)
        self.assertEqual(stderr.splitlines()[0], 'error: start too high')
        self.assertEqual(stderr.splitlines()[1], 'error: only 4 stashes exist')

    def test_abandon_startAndEnd_endBeforeStart(self):

        # test
        stdout, stderr = subprocess.Popen(
            'git abandon 5 2'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

        # verify
        self.assertFalse(stdout)
        self.assertEqual(stderr.strip(), 'error: end of range cannot come before the start')

    def test_abandon_dryRun_shortOption(self):

        # run
        abandon_output = subprocess.check_output('git abandon -d 0 2'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DRY_RUN_FORMAT.format('0', self.stash0))
        self.assertEqual(abandon_output[1], _DRY_RUN_FORMAT.format('1', self.stash1))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash0_abbrev, '0', self.initial_commit))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash1_abbrev, '1', self.initial_commit))
        self.assertEqual(stash_output[2], _STASH_FORMAT.format(self.stash2_abbrev, '2', self.initial_commit))
        self.assertEqual(stash_output[3], _STASH_FORMAT.format(self.stash3_abbrev, '3', self.initial_commit))

    def test_abandon_dryRun_longOption(self):

        # run
        abandon_output = subprocess.check_output('git abandon --dry-run 0 2'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DRY_RUN_FORMAT.format('0', self.stash0))
        self.assertEqual(abandon_output[1], _DRY_RUN_FORMAT.format('1', self.stash1))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash0_abbrev, '0', self.initial_commit))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash1_abbrev, '1', self.initial_commit))
        self.assertEqual(stash_output[2], _STASH_FORMAT.format(self.stash2_abbrev, '2', self.initial_commit))
        self.assertEqual(stash_output[3], _STASH_FORMAT.format(self.stash3_abbrev, '3', self.initial_commit))

    def test_abandon_dryRunAndQuiet(self):

        # test
        stdout, stderr = subprocess.Popen(
            'git abandon --quiet --dry-run 20'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

        # verify
        self.assertFalse(stdout)
        self.assertEqual(stderr.splitlines()[0], 'usage: git abandon [-h] [-v] [-d | -q] [START] END')
        self.assertEqual(
            stderr.splitlines()[1],
            'git abandon: error: argument -d/--dry-run: not allowed with argument -q/--quiet'
        )

    def test_abandon_quiet_shortOption(self):

        # run
        abandon_output = subprocess.check_output('git abandon -q 2'.split()).splitlines()

        # verify
        self.assertFalse(abandon_output)

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash2_abbrev, '0', self.initial_commit))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash3_abbrev, '1', self.initial_commit))

    def test_abandon_quiet_longOption(self):

        # run
        abandon_output = subprocess.check_output('git abandon --quiet 2'.split()).splitlines()

        # verify
        self.assertFalse(abandon_output)

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash2_abbrev, '0', self.initial_commit))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash3_abbrev, '1', self.initial_commit))

    def test_abandon_nonGitRepository(self):

        # setup
        os.mkdir(self.dirpath + '/dir')
        os.chdir(self.dirpath + '/dir')

        # run
        p = subprocess.Popen('git abandon -d 2'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # verify
        expected = "error: '{}' not a git repository".format(os.path.realpath(self.dirpath) + '/dir')
        self.assertEqual(expected, stderr.strip())
        self.assertFalse(stdout)

    def test_abandon_version(self):

        # expect
        self.assertRegexpMatches(self._output('git abandon -v'.split()), 'git-abandon \\d+\\.\\d+\\.\\d+')
        self.assertRegexpMatches(self._output('git abandon --version'.split()), 'git-abandon \\d+\\.\\d+\\.\\d+')

    def test_abandon_help(self):

        # expect
        self.assertTrue(self._output('git abandon -h'.split()))
        self.assertTrue(self._output('git abandon --help'.split()))
