import os
import shutil
import tempfile
import unittest

import git


class TestChangesAssociate(unittest.TestCase):

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test_associate_getAssociationWhenEmpty(self):

        # expect:
        self.assertEqual('warn: repository is empty', self.repo.git.changes('associate'))

    def test_associate_getAssociationWhenNoAssociationExists_defaultUnspecified(self):

        # given
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

        # expect
        self.assertFalse(self.repo.git.changes('associate'))

    def test_associate_getAssociationWhenNoAssociationExists_defaultUnspecified_verbose(self):

        # given
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

        # expect
        self.assertEqual('refs/heads/master', self.repo.git.changes('associate', '--verbose'))
        self.assertEqual('refs/heads/master', self.repo.git.changes('associate', '-V'))

    def test_associate_getAssociationWhenNoAssociationExists_defaultOverridden(self):

        # given: overridden default commit-ish
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')
        self.repo.git.config('--local', 'git-changes.default-commit-ish', self.repo.rev_parse('HEAD'))

        # expect
        self.assertFalse(self.repo.git.changes('associate'))

    def test_associate_getAssociationWhenNoAssociationExists_defaultOverridden_verbose(self):

        # given: overridden default commit-ish
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')
        self.repo.git.config('--local', 'git-changes.default-commit-ish', self.repo.rev_parse('HEAD'))

        # expect
        self.assertEqual(str(self.repo.rev_parse('HEAD')), self.repo.git.changes('associate', '--verbose'))
        self.assertEqual(str(self.repo.rev_parse('HEAD')), self.repo.git.changes('associate', '-V'))
