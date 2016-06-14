import os
import shutil
import subprocess
import tempfile
import unittest

_DROPPED_FORMAT = 'Dropped refs/stash@{{{}}} ({})'
_DRY_RUN_FORMAT = 'Would drop refs/stash@{{{}}} ({})'
_STASH_FORMAT = '{} refs/stash@{{{}}}: WIP on master: 7f7c6df Initial commit'


class TestGitAbandon(unittest.TestCase):

    def _stashes(self):
        return subprocess.check_output(('git', 'stash', 'list', '--oneline', '--no-color'))

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        subprocess.call('git init --quiet'.split())
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())

        # 7f7c6df
        pyenv = os.environ.copy()
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-15T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-15T20:38:31Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'], env=pyenv)
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')

        # stash@{3}: 96c2b52 96c2b52bc3736ace09920c5b6174d1fa0b2e5ad3
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-16T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-16T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())

        # stash@{2}: 860d895 860d8950ed7454b6e9aea1a528f697b704485592
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-17T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-17T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())

        # stash@{1}: 70e34df 70e34dfc65b3debd5c9ada7ec5860e3afd24bfe6
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-18T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-18T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())

        # stash@{0}: 090351f 090351fd3c783e692dc90ddeb3ee34d79005fa47
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-19T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-19T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test_abandon_endOnly(self):

        # run
        abandon_output = subprocess.check_output('git abandon 2'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('0', '090351fd3c783e692dc90ddeb3ee34d79005fa47'))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('1', '70e34dfc65b3debd5c9ada7ec5860e3afd24bfe6'))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format('860d895', '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format('96c2b52', '1'))

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
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('0', '090351fd3c783e692dc90ddeb3ee34d79005fa47'))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('1', '70e34dfc65b3debd5c9ada7ec5860e3afd24bfe6'))
        self.assertEqual(abandon_output[2], _DROPPED_FORMAT.format('2', '860d8950ed7454b6e9aea1a528f697b704485592'))
        self.assertEqual(abandon_output[3], _DROPPED_FORMAT.format('3', '96c2b52bc3736ace09920c5b6174d1fa0b2e5ad3'))
        self.assertFalse(self._stashes())

    def test_abandon_startAndEnd_all(self):

        # run
        abandon_output = subprocess.check_output('git abandon 0 4'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('0', '090351fd3c783e692dc90ddeb3ee34d79005fa47'))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('1', '70e34dfc65b3debd5c9ada7ec5860e3afd24bfe6'))
        self.assertEqual(abandon_output[2], _DROPPED_FORMAT.format('2', '860d8950ed7454b6e9aea1a528f697b704485592'))
        self.assertEqual(abandon_output[3], _DROPPED_FORMAT.format('3', '96c2b52bc3736ace09920c5b6174d1fa0b2e5ad3'))
        self.assertFalse(self._stashes())

    def test_abandon_startAndEnd_fromZero(self):

        # run
        abandon_output = subprocess.check_output('git abandon 0 2'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('0', '090351fd3c783e692dc90ddeb3ee34d79005fa47'))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('1', '70e34dfc65b3debd5c9ada7ec5860e3afd24bfe6'))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format('860d895', '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format('96c2b52', '1'))

    def test_abandon_startAndEnd_endsAtStashCount(self):

        # run
        abandon_output = subprocess.check_output('git abandon 2 4'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('2', '860d8950ed7454b6e9aea1a528f697b704485592'))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('3', '96c2b52bc3736ace09920c5b6174d1fa0b2e5ad3'))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format('090351f', '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format('70e34df', '1'))

    def test_abandon_startAndEnd_pastEnd(self):

        # run
        abandon_output = subprocess.check_output('git abandon 2 10'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('2', '860d8950ed7454b6e9aea1a528f697b704485592'))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('3', '96c2b52bc3736ace09920c5b6174d1fa0b2e5ad3'))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format('090351f', '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format('70e34df', '1'))

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
        self.assertEqual(abandon_output[0], _DRY_RUN_FORMAT.format('0', '090351fd3c783e692dc90ddeb3ee34d79005fa47'))
        self.assertEqual(abandon_output[1], _DRY_RUN_FORMAT.format('1', '70e34dfc65b3debd5c9ada7ec5860e3afd24bfe6'))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format('090351f', '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format('70e34df', '1'))
        self.assertEqual(stash_output[2], _STASH_FORMAT.format('860d895', '2'))
        self.assertEqual(stash_output[3], _STASH_FORMAT.format('96c2b52', '3'))

    def test_abandon_dryRun_longOption(self):

        # run
        abandon_output = subprocess.check_output('git abandon --dry-run 0 2'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DRY_RUN_FORMAT.format('0', '090351fd3c783e692dc90ddeb3ee34d79005fa47'))
        self.assertEqual(abandon_output[1], _DRY_RUN_FORMAT.format('1', '70e34dfc65b3debd5c9ada7ec5860e3afd24bfe6'))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format('090351f', '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format('70e34df', '1'))
        self.assertEqual(stash_output[2], _STASH_FORMAT.format('860d895', '2'))
        self.assertEqual(stash_output[3], _STASH_FORMAT.format('96c2b52', '3'))

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
        self.assertEqual(stash_output[0], _STASH_FORMAT.format('860d895', '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format('96c2b52', '1'))

    def test_abandon_quiet_longOption(self):

        # run
        abandon_output = subprocess.check_output('git abandon --quiet 2'.split()).splitlines()

        # verify
        self.assertFalse(abandon_output)

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format('860d895', '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format('96c2b52', '1'))

    def test_abandon_nonGitRepository(self):

        # setup
        os.mkdir(self.dirpath + '/dir')
        os.chdir(self.dirpath + '/dir')

        # run
        p = subprocess.Popen('git abandon -d 2'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # verify
        expected = "error: '{}' not a git repository".format('/private' + self.dirpath + '/dir')
        self.assertEqual(expected, stderr.strip())
        self.assertFalse(stdout)

    # def test_setup(self):
    #     log_output = subprocess.check_output(('git', 'log', '--oneline', '--no-color'))
    #     self.assertTrue(log_output.startswith('7f7c6df'), 'wanted {} was {}'.format('7f7c6df', log_output))
    #
    #     stash_output = subprocess.check_output('git stash list --oneline --no-color'.split()).splitlines()
    #     print stash_output
    #
    #     self.assertTrue(stash_output[0].startswith('090351f'))
    #     self.assertTrue(stash_output[1].startswith('70e34df'))
    #     self.assertTrue(stash_output[2].startswith('860d895'))
    #     self.assertTrue(stash_output[3].startswith('96c2b52'))
    #
    #     self.assertEqual(stash_output[3], '96c2b52 refs/stash@{3}: WIP on master: 7f7c6df Initial commit')
