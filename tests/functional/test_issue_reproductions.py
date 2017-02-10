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
