import os
import shutil
import tempfile
import unittest
from subprocess import call, check_output, PIPE, Popen, STDOUT


class TestGitSnapshot(unittest.TestCase):

    def _status(self):
        return check_output(('git', '-c', 'color.ui=never', 'status', '--short'))

    def _stashes(self):
        return check_output(('git', 'stash', 'list')).splitlines()

    def _output(self, command):
        proc = Popen(command, stdout=PIPE, stderr=STDOUT)
        return proc.communicate()[0].strip()

    def setUp(self):

        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        call('git init --quiet'.split())
        call('touch CHANGELOG.md'.split())
        call('touch CONTRIBUTING.md'.split())
        call('git add -A'.split())
        call(['git', 'commit', '--quiet', '-m', 'Initial commit'])

        with open('CHANGELOG.md', 'w') as a_file:
            a_file.write('changelog\n')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test_snapshot(self):

        # run
        stdout, stderr = Popen('git snapshot'.split(), stdout=PIPE, stderr=PIPE).communicate()

        # verify
        self.assertRegexpMatches(stdout.strip(), 'Saved working directory and index state WIP on master: \w+ Initial commit')
        self.assertFalse(stderr)
        self.assertEqual(self._status(), " M CHANGELOG.md\n")

        stashes = self._stashes()
        self.assertEqual(len(stashes), 1)
        self.assertRegexpMatches(stashes[0], 'stash@\{0\}: WIP on master: [0-9a-f]+ Initial commit')

        call('git reset --hard --quiet'.split())
        call('git stash pop --quiet'.split())
        self.assertEqual(self._status(), " M CHANGELOG.md\n")

    def test_snapshot_quiet(self):

        # run
        stdout, stderr = Popen('git snapshot --quiet'.split(), stdout=PIPE, stderr=PIPE).communicate()

        # verify
        self.assertFalse(stdout)
        self.assertFalse(stderr)
        self.assertEqual(self._status(), " M CHANGELOG.md\n")

        stashes = self._stashes()
        self.assertEqual(len(stashes), 1)
        self.assertRegexpMatches(stashes[0], 'stash@\{0\}: WIP on master: [0-9a-f]+ Initial commit')

        call('git reset --hard --quiet'.split())
        call('git stash pop --quiet'.split())
        self.assertEqual(self._status(), " M CHANGELOG.md\n")

    def test_snapshot_complex(self):

        # setup
        call('touch CONTRIBUTING.md'.split())
        call('touch README.md'.split())
        call('touch file1.txt'.split())
        call('touch file2.txt'.split())
        with open('CONTRIBUTING.md', 'w') as a_file:
            a_file.write('contributing\n')
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        with open('file0.txt', 'w') as a_file:
            a_file.write('file0\n')
        with open('file1.txt', 'w') as a_file:
            a_file.write('file1\n')
        with open('file2.txt', 'w') as a_file:
            a_file.write('file2\n')
        call('git add -A'.split())
        call(['git', 'commit', '--quiet', '--message', 'Initial commit'])

        call('rm file0.txt'.split())
        call(['git', 'commit', '--all', '--quiet', '--message', 'Remove file0.txt'])

        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')
        call('git add -- CHANGELOG.md'.split())
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')

        with open('CONTRIBUTING.md', 'a') as a_file:
            a_file.write('contributing\n')
        call('git add -- CONTRIBUTING.md'.split())

        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')

        call('git rm --quiet -- file1.txt'.split())
        call('rm file2.txt'.split())
        call('touch file3.txt'.split())
        call('git add -- file3.txt'.split())
        call('touch file4.txt'.split())

        # MM CHANGELOG.md
        # M  CONTRIBUTING.md
        #  M README.md
        # D  file1.txt
        #  D file2.txt
        # A  file3.txt
        # ?? file4.txt

        # run
        call('git snapshot --quiet'.split())

        # verify
        call('git reset --hard --quiet'.split())
        call('git clean --force --quiet'.split())
        call('git stash pop --index --quiet'.split())
        self.assertEqual(self._status(), """MM CHANGELOG.md
M  CONTRIBUTING.md
 M README.md
D  file1.txt
 D file2.txt
A  file3.txt
?? file4.txt
""")

    def test_snapshot_withMessage(self):

        # setup
        message = "My snapshot message"

        # run
        stdout, stderr = Popen(('git', 'snapshot', message), stdout=PIPE, stderr=PIPE).communicate()

        # verify
        self.assertEqual(stdout.strip(), 'Saved working directory and index state On master: My snapshot message')
        self.assertFalse(stderr)
        self.assertEqual(self._status(), " M CHANGELOG.md\n")

        stashes = self._stashes()
        self.assertEqual(len(stashes), 1)
        self.assertRegexpMatches(stashes[0], 'stash@\{0\}: On master: ' + message)

        call('git reset --hard --quiet'.split())
        call('git stash pop --quiet'.split())
        self.assertEqual(self._status(), " M CHANGELOG.md\n")

    def test_snapshot_quiet(self):

        # run
        stdout, stderr = Popen('git snapshot --quiet'.split(), stdout=PIPE, stderr=PIPE).communicate()

        # verify
        self.assertFalse(stdout)
        self.assertFalse(stderr)

    def test_snapshot_quiet_shortOption(self):

        # run
        stdout, stderr = Popen('git snapshot -q'.split(), stdout=PIPE, stderr=PIPE).communicate()

        # verify
        self.assertFalse(stdout)
        self.assertFalse(stderr)

    def test_snapshot_specificFiles(self):

        # setup
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')

        # run
        call('git snapshot --quiet -- CHANGELOG.md'.split())

        # verify
        self.assertEqual(self._status(), " M CHANGELOG.md\n?? README.md\n")

        call('git reset --hard --quiet'.split())
        call('git clean --force --quiet'.split())
        call('git stash pop --quiet'.split())
        self.assertEqual(self._status(), " M CHANGELOG.md\n")

    def test_snapshot_noChanges(self):

        # setup
        call('git reset --hard --quiet'.split())

        # run
        result = check_output('git snapshot'.split())

        # verify
        self.assertEqual(result.strip(), 'No local changes to save. No snapshot created.')

    def test_snapshot_noChanges_quiet(self):

        # setup
        call('git reset --hard --quiet'.split())

        # run
        stdout, stderr = Popen('git snapshot --quiet'.split(), stdout=PIPE, stderr=PIPE).communicate()

        # verify
        self.assertFalse(stdout)
        self.assertFalse(stderr)

    def test_snapshot_noChanges_quiet_shortOption(self):

        # setup
        call('git reset --hard --quiet'.split())

        # run
        stdout, stderr = Popen('git snapshot -q'.split(), stdout=PIPE, stderr=PIPE).communicate()

        # verify
        self.assertFalse(stdout)
        self.assertFalse(stderr)

    def test_snapshot_nonGitRepository(self):

        # setup
        os.mkdir(self.dirpath + '/dir')
        os.chdir(self.dirpath + '/dir')

        # run
        p = Popen('git snapshot'.split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        # verify
        expected = "error: '{}' not a git repository".format(os.path.realpath(self.dirpath) + '/dir')
        self.assertEqual(expected, stderr.strip())
        self.assertFalse(stdout)

    def test_snapshot_version(self):

        # expect
        self.assertRegexpMatches(self._output('git snapshot -v'.split()), 'git-snapshot \\d+\\.\\d+\\.\\d+')
        self.assertRegexpMatches(self._output('git snapshot --version'.split()), 'git-snapshot \\d+\\.\\d+\\.\\d+')

    def test_snapshot_help(self):

        # expect
        self.assertTrue(self._output('git snapshot -h'.split()))
        self.assertTrue(self._output('git snapshot --help'.split()))

    def test_snapshot_replace(self):

        # given
        message = "My snapshot message"
        self._output('git reset --hard'.split())
        self._output('git stash drop'.split())
        with open('CONTRIBUTING.md', 'w') as a_file:
            a_file.write('contributing\n')

        # when
        stdout, stderr = Popen(('git', 'snapshot', '--replace', message), stdout=PIPE, stderr=PIPE).communicate()

        # then
        self.assertEqual(stdout.strip(), 'Saved working directory and index state On master: My snapshot message')
        self.assertFalse(stderr)
        self.assertEqual(self._status(), " M CONTRIBUTING.md\n")

        stashes = self._stashes()
        self.assertEqual(len(stashes), 1)
        self.assertRegexpMatches(stashes[0], 'stash@\{0\}: On master: ' + message)

        call('git reset --hard --quiet'.split())
        call('git stash pop --quiet'.split())
        self.assertEqual(self._status(), " M CONTRIBUTING.md\n")

    def test_snapshot_replaceWithoutMessage(self):

        # when
        stdout, stderr = Popen(('git', 'snapshot', '--replace'), stdout=PIPE, stderr=PIPE).communicate()

        # then
        self.assertEqual(stdout.strip(), 'usage: git snapshot [MESSAGE] [-h] [-v] [-r] [-q] [-- FILE [FILE ...]]')
        self.assertEqual(stderr.strip(), 'git snapshot: error: argument -r/--replace: not allowed without positional argument message')
