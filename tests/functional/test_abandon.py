import os
import shutil
import subprocess
import tempfile
import unittest

_DROPPED_FORMAT = 'Dropped refs/stash@{{{}}} ({})'
_DRY_RUN_FORMAT = 'Would drop refs/stash@{{{}}} ({})'
_STASH_FORMAT = '{} refs/stash@{{{}}}: WIP on master: 001c499 Initial commit'


class TestGitAbandon(unittest.TestCase):

    def _stashes(self):
        return subprocess.check_output(('git', 'stash', 'list', '--oneline', '--no-color'))

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        subprocess.call('git init --quiet'.split())
        subprocess.call('git config --local user.name username'.split())
        subprocess.call('git config --local user.mail username@mail.com'.split())
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())

        # 001c499 001c499d1f0503e95bc452f41c5cd9de5d735e15
        pyenv = os.environ.copy()
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-15T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-15T20:38:31Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'], env=pyenv)
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')

        # stash@{3}
        self.stash3 = '548a8f32b37f8f08ba89b52b400575bba222778a'
        self.stash3_abbrev = '548a8f3'
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-16T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-16T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())

        # stash@{2}
        self.stash2 = 'e4fd7148a47afa483cfac68ad7a96dd82f1a0083'
        self.stash2_abbrev = 'e4fd714'
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-17T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-17T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())

        # stash@{1}
        self.stash1 = '4e12234d05e22c2d3aa970ec25be3147b402b3bc'
        self.stash1_abbrev = '4e12234'
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-18T20:38:31Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-18T20:38:31Z'
        subprocess.call('git stash --quiet'.split(), env=pyenv)
        subprocess.call('git stash apply --quiet'.split())

        # stash@{0}
        self.stash0 = '3ef3f6941016f472341d0ca081320556c41842e3'
        self.stash0_abbrev = '3ef3f69'
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
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('0', self.stash0))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('1', self.stash1))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash2_abbrev, '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash3_abbrev, '1'))

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
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash2_abbrev, '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash3_abbrev, '1'))

    def test_abandon_startAndEnd_endsAtStashCount(self):

        # run
        abandon_output = subprocess.check_output('git abandon 2 4'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('2', self.stash2))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('3', self.stash3))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash0_abbrev, '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash1_abbrev, '1'))

    def test_abandon_startAndEnd_pastEnd(self):

        # run
        abandon_output = subprocess.check_output('git abandon 2 10'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DROPPED_FORMAT.format('2', self.stash2))
        self.assertEqual(abandon_output[1], _DROPPED_FORMAT.format('3', self.stash3))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash0_abbrev, '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash1_abbrev, '1'))

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
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash0_abbrev, '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash1_abbrev, '1'))
        self.assertEqual(stash_output[2], _STASH_FORMAT.format(self.stash2_abbrev, '2'))
        self.assertEqual(stash_output[3], _STASH_FORMAT.format(self.stash3_abbrev, '3'))

    def test_abandon_dryRun_longOption(self):

        # run
        abandon_output = subprocess.check_output('git abandon --dry-run 0 2'.split()).splitlines()

        # verify
        self.assertEqual(abandon_output[0], _DRY_RUN_FORMAT.format('0', self.stash0))
        self.assertEqual(abandon_output[1], _DRY_RUN_FORMAT.format('1', self.stash1))

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash0_abbrev, '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash1_abbrev, '1'))
        self.assertEqual(stash_output[2], _STASH_FORMAT.format(self.stash2_abbrev, '2'))
        self.assertEqual(stash_output[3], _STASH_FORMAT.format(self.stash3_abbrev, '3'))

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
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash2_abbrev, '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash3_abbrev, '1'))

    def test_abandon_quiet_longOption(self):

        # run
        abandon_output = subprocess.check_output('git abandon --quiet 2'.split()).splitlines()

        # verify
        self.assertFalse(abandon_output)

        stash_output = self._stashes().splitlines()
        self.assertEqual(stash_output[0], _STASH_FORMAT.format(self.stash2_abbrev, '0'))
        self.assertEqual(stash_output[1], _STASH_FORMAT.format(self.stash3_abbrev, '1'))

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
