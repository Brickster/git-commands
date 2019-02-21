import os
import shutil
import subprocess
import tempfile
import unittest

import git


class TestGitRestash(unittest.TestCase):

    def _output(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].strip()

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)

        # add files
        open('README.md', 'w').close()
        open('CHANGELOG.md', 'w').close()
        self.repo.index.add(['README.md', 'CHANGELOG.md'])
        self.repo.index.commit('Initial commit')

        # edit README
        with open('README.md', 'w') as readme_file:
            readme_file.write('a')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test_restash_full(self):

        # given
        self.repo.git.stash()
        self.repo.git.stash('apply')

        # when
        restash_output = self.repo.git.restash()

        # then
        stash_sha = self.repo.git.rev_parse('stash@{0}')
        self.assertEqual(restash_output, 'Restashed stash@{{0}} ({})'.format(stash_sha))
        self.assertFalse(subprocess.check_output('git status --short'.split()).strip())

    def test_restash_partial(self):

        # given
        self.repo.git.stash()
        self.repo.git.stash('apply')
        with open('CHANGELOG.md', 'w') as readme_file:
            readme_file.write('a')

        # when
        restash_output = self.repo.git.restash()

        # then
        stash_sha = self.repo.git.rev_parse('stash@{0}')
        self.assertEqual(restash_output, 'Restashed stash@{{0}} ({})'.format(stash_sha))
        status_output = subprocess.check_output('git -c color.ui=never status --short'.split()).rstrip()
        self.assertEqual(status_output, ' M CHANGELOG.md')

    def test_restash_specifyStash(self):

        # given
        self.repo.git.stash()
        self.repo.git.stash('apply')
        with open('CHANGELOG.md', 'w') as readme_file:
            readme_file.write('a')
        self.repo.git.stash()
        self.repo.git.stash('apply')

        # when
        restash_output = self.repo.git.restash('stash@{1}')

        # then
        stash_sha = self.repo.git.rev_parse('stash@{1}')
        self.assertEqual(restash_output, 'Restashed stash@{{1}} ({})'.format(stash_sha))
        status_output = subprocess.check_output('git -c color.ui=never status --short'.split()).rstrip()
        self.assertEqual(status_output, ' M CHANGELOG.md')

    def test_restash_withNewFiles(self):

        # given
        open('CONTRIBUTING.md', 'w').close()
        self.repo.git.stash('save', '--include-untracked')
        self.repo.git.stash('apply')

        # when
        restash_output = self.repo.git.restash()

        # then
        stash_sha = self.repo.git.rev_parse('stash@{0}')
        self.assertEqual(restash_output, 'Restashed stash@{{0}} ({})'.format(stash_sha))
        self.assertFalse(subprocess.check_output('git status --short'.split()).strip())

    def test_restash_withDeletedFiles(self):

        # given
        os.remove('CHANGELOG.md')
        self.repo.git.stash('save', '--include-untracked')
        self.repo.git.stash('apply')

        # when
        restash_output = self.repo.git.restash()

        # then
        stash_sha = self.repo.git.rev_parse('stash@{0}')
        self.assertEqual(restash_output, 'Restashed stash@{{0}} ({})'.format(stash_sha))
        self.assertFalse(subprocess.check_output('git status --short'.split()).strip())

    def test_restash_quiet_shortOption(self):

        # given
        self.repo.git.stash()
        self.repo.git.stash('apply')

        # when
        restash_output = self.repo.git.restash('-q')

        # then
        self.assertFalse(restash_output)

    def test_restash_quiet_longOption(self):

        # given
        self.repo.git.stash()
        self.repo.git.stash('apply')

        # when
        restash_output = self.repo.git.restash('--quiet')

        # then
        self.assertFalse(restash_output)

    def test_restash_noStashesExist(self):

        # when
        error_message = subprocess.Popen(
            'git restash blarg'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()[1].strip()

        # then
        self.assertEqual(error_message, 'error: no stashes exist')

    def test_restash_invalidStash(self):

        # given
        self.repo.git.stash()

        # when
        error_message = subprocess.Popen(
            'git restash blarg'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()[1].strip()

        # then
        self.assertEqual(error_message, 'error: blarg is not a valid stash reference')

    def test_restash_nonGitRepository(self):

        # setup
        os.mkdir(self.dirpath + '/dir')
        os.chdir(self.dirpath + '/dir')

        # run
        p = subprocess.Popen('git restash'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # verify
        expected = "error: '{}' not a git repository".format(os.path.realpath(self.dirpath) + '/dir')
        self.assertEqual(expected, stderr.strip())
        self.assertFalse(stdout)

    def test_restash_version(self):

        # expect
        self.assertRegexpMatches(self._output('git restash -v'.split()), 'git-restash \\d+\\.\\d+\\.\\d+')
        self.assertRegexpMatches(self._output('git restash --version'.split()), 'git-restash \\d+\\.\\d+\\.\\d+')

    def test_restash_help(self):

        # expect
        self.assertTrue(self._output('git restash -h'.split()))
        self.assertTrue(self._output('git restash --help'.split()))
