import os
import shutil
import subprocess
import tempfile
import unittest

import git


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
        """Nothing should be returned if no association exists."""

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
        """Nothing should happen when pruning with no associations at all."""

        self.assertFalse(subprocess.check_output('git changes unassociate --prune'.split(), stderr=subprocess.STDOUT).strip())