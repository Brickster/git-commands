import os
import shutil
import subprocess
import tempfile
import unittest


class TestGitReindex(unittest.TestCase):

    def _reindex(self):
        return subprocess.check_output(('git', 'reindex')).decode('utf-8')

    def _status(self):
        return subprocess.check_output(('git', '-c', 'color.ui=never', 'status', '--short')).decode('utf-8')

    def _output(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].decode('utf-8').strip()

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        subprocess.call('git init --quiet'.split())
        subprocess.call('touch CHANGELOG.md'.split())
        subprocess.call('touch README.md'.split())
        with open('CHANGELOG.md', 'w') as a_file:
            a_file.write('changelog\n')
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_reindex(self):

        # setup
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')
        subprocess.call('git add -A'.split())
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog2\n')
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')

        # run
        reindex_result = self._reindex()

        # verify
        self.assertFalse(bool(reindex_result))
        self.assertEqual('M  CHANGELOG.md\n M README.md\n', self._status())

    def test_reindex_workingTreeIsCleaning(self):

        self.assertFalse(bool(self._reindex()))
        self.assertFalse(bool(self._status()))

    def test_reindex_indexIsEmpty(self):

        # setup
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')

        # run
        reindex_result = self._reindex()

        # verify
        self.assertFalse(bool(reindex_result))
        self.assertEqual(' M CHANGELOG.md\n', self._status())

    def test_reindex_indexUpToDate(self):

        # setup
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')
        subprocess.call('git add -A'.split())

        # run
        reindex_result = self._reindex()

        # verify
        self.assertFalse(bool(reindex_result))
        self.assertEqual('M  CHANGELOG.md\n', self._status())

    def test_reindex_nonGitRepository(self):

        # setup
        os.mkdir(self.dirpath + '/dir')
        os.chdir(self.dirpath + '/dir')

        # run
        p = subprocess.Popen('git reindex'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = [x.decode('utf-8') for x in p.communicate()]

        # verify
        expected = "error: '{}' not a git repository".format(os.path.realpath(self.dirpath) + '/dir')
        self.assertEqual(expected, stderr.strip())
        self.assertFalse(stdout)

    def test_reindex_deletedFile_unindexed(self):

        # setup:
        # MM CHANGELOG.md
        #  D README.md
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')
        subprocess.call('git add --all'.split())
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog2\n')
        subprocess.call('rm README.md'.split())

        reindex_result = self._reindex()

        self.assertFalse(reindex_result)
        self.assertEqual("M  CHANGELOG.md\n D README.md\n", self._status())

    def test_reindex_deletedFile_indexed(self):

        # setup:
        # MM CHANGELOG.md
        # D  README.md
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')
        subprocess.call('git add --all'.split())
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog2\n')
        subprocess.call('git rm --quiet README.md'.split())

        reindex_result = self._reindex()

        self.assertFalse(reindex_result)
        self.assertEqual("M  CHANGELOG.md\nD  README.md\n", self._status())

    def test_reindex_deletedFile_modificationInIndexAndDeleteUnindexed(self):

        # setup:
        # MD README.md
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add --all'.split())
        subprocess.call('rm README.md'.split())

        reindex_result = self._reindex()

        self.assertFalse(reindex_result)
        self.assertEqual("D  README.md\n", self._status())

    def test_reindex_newFile_unindexed(self):

        # setup:
        # MM CHANGELOG.md
        # ?? new.txt
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')
        subprocess.call('git add --all'.split())
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog2\n')
        subprocess.call('touch new.txt'.split())

        reindex_result = self._reindex()

        self.assertFalse(reindex_result)
        self.assertEqual("M  CHANGELOG.md\n?? new.txt\n", self._status())

    def test_reindex_newFile_indexed(self):

        # setup:
        # MM CHANGELOG.md
        # A  new.txt
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')
        subprocess.call('touch new.txt'.split())
        subprocess.call('git add --all'.split())
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog2\n')

        reindex_result = self._reindex()

        self.assertFalse(reindex_result)
        self.assertEqual("M  CHANGELOG.md\nA  new.txt\n", self._status())

    def test_reindex_newFile_indexedAndUnindexed(self):

        # setup:
        # MM CHANGELOG.md
        # AM new.txt
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')
        subprocess.call('touch new.txt'.split())
        subprocess.call('git add --all'.split())
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog2\n')
        with open('new.txt', 'a') as a_file:
            a_file.write('new\n')

        reindex_result = self._reindex()

        self.assertFalse(reindex_result)
        self.assertEqual("M  CHANGELOG.md\nA  new.txt\n", self._status())

    def test_reindex_version(self):

        # expect
        self.assertRegexpMatches(self._output('git reindex -v'.split()), 'git-reindex \\d+\\.\\d+\\.\\d+')
        self.assertRegexpMatches(self._output('git reindex --version'.split()), 'git-reindex \\d+\\.\\d+\\.\\d+')

    def test_reindex_help(self):

        # expect
        self.assertTrue(self._output('git reindex -h'.split()))
        self.assertTrue(self._output('git reindex --help'.split()))
