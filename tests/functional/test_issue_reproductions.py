import os
import shutil
import subprocess
import tempfile
import unittest

import git


class TestIssue093(unittest.TestCase):
    """State --no-status not respected for new repositories"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 93: --no-status should be respected even for new repositories"""

        self.assertFalse(self.repo.git.state('--no-status'))


class TestIssue094(unittest.TestCase):
    """Changes breaks when HEAD is detached"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repositorygit stat
        repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        repo.index.add(['README.md'])
        repo.index.commit('Initial commit')
        open('CONTRIBUTING.md', 'w').close()
        repo.index.add(['CONTRIBUTING.md'])
        repo.index.commit('Add CONTRIBUTING.md')

        # detach head
        repo.git.changes('associate', 'HEAD~1')
        repo.git.checkout('HEAD~1')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 094: Changes should be returned even if head is detached"""

        self.assertFalse(subprocess.check_output('git changes'.split(), stderr=subprocess.STDOUT).strip())


class TestIssue102(unittest.TestCase):
    """
    `changes unassociate` fails when no association exists

    ```
    $ git changes associate
    $ git changes unassociate
    fatal: No such section!
    ```

    https://github.com/Brickstertwo/git-commands/issues/102
    """

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        git.Repo.init(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 102: Nothing should be returned if no association exists."""

        self.assertFalse(subprocess.check_output('git changes unassociate'.split(), stderr=subprocess.STDOUT).strip())


class TestIssue103(unittest.TestCase):
    """`changes unassociate --prune` fails when no association exist for any branch"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        repo.index.add(['README.md'])
        repo.index.commit('Initial commit')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 103: Nothing should happen when pruning with no associations at all."""

        self.assertFalse(subprocess.check_output('git changes unassociate --prune'.split(), stderr=subprocess.STDOUT).strip())


class TestIssue104(unittest.TestCase):
    """`changes unassociate --prune` fails for new repositories"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        git.Repo.init(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 104: Nothing should happen when pruning a new repository."""

        self.assertFalse(
            subprocess.check_output('git changes unassociate --prune'.split(), stderr=subprocess.STDOUT).strip())


class TestIssue106(unittest.TestCase):
    """Associating when detached uses HEAD as branch"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repositorygit stat
        repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        repo.index.add(['README.md'])
        repo.index.commit('Initial commit')
        open('CONTRIBUTING.md', 'w').close()
        repo.index.add(['CONTRIBUTING.md'])
        repo.index.commit('Add CONTRIBUTING.md')

        # detach head
        repo.git.changes('associate', 'HEAD~1')
        repo.git.checkout('HEAD~1')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 106: Do not allow associating a detached HEAD"""

        associate_proc = subprocess.Popen(('git', 'changes', 'associate', 'HEAD'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = associate_proc.communicate()
        self.assertFalse(stdout)
        self.assertEqual(stderr.strip(), 'error: cannot associate while HEAD is detached')


class TestIssue107(unittest.TestCase):
    """Associate blows up on invalid revision"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 107: an error should be printed when associating with an invalid revision"""

        bad_revision = 'bad_rev'
        error = subprocess.Popen(['git', 'changes', 'associate', bad_revision], stderr=subprocess.PIPE).communicate()[1].strip()
        self.assertEqual(error, 'error: {} is not a valid revision'.format(bad_revision))


class TestIssue108(unittest.TestCase):
    """Dry running an unassociate without an association print misleading result"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 108: Dry running an unassociate without an association should print nothing"""

        self.assertFalse(subprocess.check_output('git changes unassociate --dry-run'.split()).strip())
