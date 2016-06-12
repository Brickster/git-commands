import os
import shutil
import subprocess
import tempfile
import unittest


class TestGitReindex(unittest.TestCase):

    def _reindex(self):
        return subprocess.check_output(('git', 'reindex'))

    def _status(self):
        return subprocess.check_output(('git', '-c', 'color.ui=never', 'status', '--short'))

    def setUp(self):
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
        stdout, stderr = p.communicate()

        # verify
        expected = "error: '{}' not a git repository".format('/private' + self.dirpath + '/dir')
        self.assertEqual(expected, stderr.strip())
        self.assertFalse(stdout)
