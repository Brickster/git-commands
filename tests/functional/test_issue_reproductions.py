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

        # initialize repository
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


class TestIssue095(unittest.TestCase):
    """Settings list fails if a value contains a newline"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

        # add config with newline
        os.remove(self.dirpath + '/.git/config')
        self.repo.git.config('test.withnewline', """ab
c""")

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 95: settings list should handle values with newlines"""

        self.assertEqual(self.repo.git.settings('list', '--local'), """test.withnewline=ab
c""")


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


class TestIssue105(unittest.TestCase):
    """
    Tucking new files occasionally prints an error but ultimately works.

    Due to the nature of this issue the tests are not very efficient. Meaning, they need to run enough times to be
    confident the issue would occur.
    """

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

        # add a new file
        open('CHANGELOG.md', 'w').close()

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 105: tucking new files should never print more detail than a stash would"""

        for i in xrange(5):
            tuck_output = self.repo.git.tuck('--', 'CHANGELOG.md')
            self.assertNotIn("error: pathspec 'CONTRIBUTING.md' did not match any file(s) known to git.", tuck_output)
            self.assertNotIn('Already up-to-date!', tuck_output)
            self.assertEqual(2, len(tuck_output.splitlines()))
            self.repo.git.stash('pop')


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


class TestIssue111(unittest.TestCase):
    """Snapshotting specific files with a message should snapshot successfully"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

        # edit a file
        with open('README.md', 'w') as readme_file:
            readme_file.write('a')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 111: Unable to include files and message in snapshot"""

        self.assertFalse(subprocess.check_output('git snapshot "md files" -- *.md'.split()).strip())
        self.assertEqual(1, len(subprocess.check_output('git stash list'.split()).strip().split('\n')))


class TestIssue112(unittest.TestCase):
    """Associating with a local upstream should associate with refs/head/<<UPSTREAM>>"""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

        # checkout new develop branch with master as its upstream
        self.repo.create_head('develop', 'HEAD')
        self.repo.heads.develop.checkout()
        self.repo.git.branch(set_upstream_to='master')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):
        """Issue 112: Associate --upstream fails for local upstream"""

        self.assertEqual(
            subprocess.check_output('git changes associate --upstream'.split()).strip(),
            'develop has been associated with refs/heads/master'
        )


class TestIssue113(unittest.TestCase):
    """Dry running a tuck for a commonly named file should only report that file in the dry run."""

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        os.mkdir(self.dirpath + '/files')
        open('files/README.md', 'w').close()
        self.repo.index.add(['README.md', 'files/README.md'])
        self.repo.index.commit('Initial commit')

        # edit files
        with open('README.md', 'w') as readme_file:
            readme_file.write('a')
        with open('files/README.md', 'w') as readme_file:
            readme_file.write('a')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test(self):

        expected = """Would tuck:

     M README.md

Leaving working directory:

     M files/README.md

"""
        self.assertEqual(subprocess.check_output('git tuck --dry-run --no-color -- README.md'.split()), expected)


class TestIssue115(unittest.TestCase):
    """
    Tuck occasionally drops unrelated stashes

    Due to the nature of this issue the tests are not very efficient. Meaning, they need to run enough times to be
    confident the issue would occur.
    """

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository with a README
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

        # edit the README and snapshot it
        with open('README.md', 'w') as readme_file:
            readme_file.write('a')
        self.repo.git.stash()
        self.repo.git.stash('apply')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test_unnamed(self):
        """Issue 114: Tuck should never remove previous stashes when unnamed"""

        for i in xrange(5):
            self.repo.git.tuck('--', 'README.md')
            self.repo.git.stash('pop')

        stashes = self.repo.git.stash('list').splitlines()
        self.assertEqual(len(stashes), 1)

    def test_named(self):
        """Issue 114: Tuck should never remove previous stashes when named"""

        for i in xrange(5):
            self.repo.git.tuck('snapshot', '--', 'README.md')
            self.repo.git.stash('pop')

        stashes = self.repo.git.stash('list').splitlines()
        self.assertEqual(len(stashes), 1)
