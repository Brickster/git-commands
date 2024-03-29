import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import git

from . import testutils
from ..layers import Issues


class TestIssue093(unittest.TestCase):
    """State --no-status not respected for new repositories"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 93: hiding status should be respected even for new repositories"""

        self.assertFalse(self.repo.git.state('--no-show status'.split()))


class TestIssue094(unittest.TestCase):
    """Changes breaks when HEAD is detached"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
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
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 094: Changes should be returned even if head is detached"""

        self.assertFalse(subprocess.check_output('git changes'.split(), stderr=subprocess.STDOUT).strip())


class TestIssue095(unittest.TestCase):
    """Settings list fails if a value contains a newline"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
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
        os.chdir(self.proj_dir)

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

    https://github.com/Brickster/git-commands/issues/102
    """
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        repo.index.add(['README.md'])
        repo.index.commit('Initial commit')

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 102: Nothing should be returned if no association exists."""

        self.assertFalse(subprocess.check_output('git changes unassociate'.split(), stderr=subprocess.STDOUT).strip())


class TestIssue103(unittest.TestCase):
    """`changes unassociate --prune` fails when no association exist for any branch"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        repo.index.add(['README.md'])
        repo.index.commit('Initial commit')

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 103: Nothing should happen when pruning with no associations at all."""

        self.assertFalse(subprocess.check_output('git changes unassociate --prune'.split(), stderr=subprocess.STDOUT).strip())


class TestIssue104(unittest.TestCase):
    """`changes unassociate --prune` fails for new repositories"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        git.Repo.init(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 104: Nothing should happen when pruning a new repository."""

        self.assertFalse(
            subprocess.check_output('git changes unassociate --prune'.split(), stderr=subprocess.STDOUT).strip())


class TestIssue106(unittest.TestCase):
    """Associating when detached uses HEAD as branch"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
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
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 106: Do not allow associating a detached HEAD"""

        associate_proc = subprocess.Popen(('git', 'changes', 'associate', 'HEAD'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = [x.decode('utf-8') for x in associate_proc.communicate()]
        self.assertFalse(stdout)
        self.assertEqual(stderr.strip(), 'error: cannot associate while HEAD is detached')


class TestIssue107(unittest.TestCase):
    """Associate blows up on invalid revision"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 107: an error should be printed when associating with an invalid revision"""

        bad_revision = 'bad_rev'
        error = subprocess.Popen(['git', 'changes', 'associate', bad_revision], stderr=subprocess.PIPE).communicate()[1].decode('utf-8').strip()
        self.assertEqual(error, 'error: {} is not a valid revision'.format(bad_revision))


class TestIssue108(unittest.TestCase):
    """Dry running an unassociate without an association print misleading result"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 108: Dry running an unassociate without an association should print nothing"""

        self.assertFalse(subprocess.check_output('git changes unassociate --dry-run'.split()).strip())


class TestIssue111(unittest.TestCase):
    """Snapshotting specific files with a message should snapshot successfully"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
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
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 111: Unable to include files and message in snapshot"""

        self.assertFalse(subprocess.check_output('git snapshot --quiet "md files" -- *.md'.split()).strip())
        self.assertEqual(1, len(subprocess.check_output('git stash list'.split()).decode('utf-8').strip().split('\n')))


class TestIssue112(unittest.TestCase):
    """Associating with a local upstream should associate with refs/head/<<UPSTREAM>>"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
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
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 112: Associate --upstream fails for local upstream"""

        self.assertEqual(
            subprocess.check_output('git changes associate --upstream'.split()).decode('utf-8').strip(),
            'develop has been associated with refs/heads/master'
        )


class TestIssue114(unittest.TestCase):
    """Snapshot occasionally does nothing."""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository with a README
        self.repo = git.Repo.init(self.dirpath)
        open('README.md', 'w').close()
        os.mkdir(self.dirpath + '/files')
        open('files/README.md', 'w').close()
        self.repo.index.add(['README.md', 'files/README.md'])
        self.repo.index.commit('Initial commit')

        # edit the README
        with open('README.md', 'w') as readme_file:
            readme_file.write('a')

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 114: quickly creating n snapshots should create n stashes."""

        self.repo.git.snapshot()
        self.repo.git.snapshot()
        self.repo.git.snapshot()
        self.repo.git.snapshot()
        self.repo.git.snapshot()
        self.repo.git.snapshot()
        self.repo.git.snapshot()

        stashes = self.repo.git.stash('list').splitlines()
        self.assertEqual(len(stashes), 7)


class TestIssue119(unittest.TestCase):
    """Limiting settings to keys should require a section"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        settings_proc = subprocess.Popen(
            'git settings list --keys'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = [x.decode('utf-8') for x in settings_proc.communicate()]
        self.assertFalse(stdout)
        self.assertEqual(stderr.strip(), 'error: argument -k/--keys: not allowed without positional argument section')


class TestIssue121(unittest.TestCase):
    """Settings list fails when the config file is empty"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        os.remove(self.dirpath + '/.git/config')
        open(self.dirpath + '/.git/config', 'w').close()

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 121: settings list should not fail with blank config files"""

        self.assertFalse(self.repo.git.settings('list', '--local'))
        self.assertFalse(self.repo.git.settings('list', '--file', self.dirpath + '/.git/config'))


class TestIssue122(unittest.TestCase):
    """Settings list does not gracefully handle unknown files"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 122: settings list should gracefully print unknown file errors"""

        settings_proc = subprocess.Popen(
            'git settings list --file unknown_file'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = [x.decode('utf-8') for x in settings_proc.communicate()]
        self.assertFalse(stdout)
        self.assertEqual(stderr.strip(), "error: no such file 'unknown_file'")


class TestIssue124(unittest.TestCase):
    """`git changes` decoration differs when printing to a terminal"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository with a README
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

        # make changes
        with open('README.md', 'w') as readme_file:
            readme_file.write('readme')
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Edit readme')
        self.commit0_log = subprocess.check_output('git rev-parse --short HEAD'.split()).decode('utf-8').strip() + ' Edit readme'

        # make sure coloring isn't enabled
        subprocess.call(['git', 'config', '--local', 'color.ui', 'auto'])

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 124: git-changes should not decorate when printing to a TTY"""

        # NOTE: this test never failed since stdout is not a TTY and I couldn't figure out how to fake it. I'm leaving
        # this here anyway.
        # expect
        self.assertEqual(self.commit0_log, self.repo.git.changes('HEAD^'))


@unittest.skipIf(
    '--no-skip' not in sys.argv,
    'requires editing user config and should only run during non-local builds.'
)
class TestIssue131(unittest.TestCase):
    """Handle missing system config when using git-settings list"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 131: a missing config file should print nothing"""

        # given: no system config
        if os.path.exists('/etc/gitconfig'):
            os.remove('/etc/gitconfig')
        if os.path.exists('/usr/local/etc/gitconfig'):
            os.remove('/usr/local/etc/gitconfig')

        # when
        settings_proc = subprocess.Popen(
            'git settings list --system'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout = settings_proc.communicate()[0]

        # then
        self.assertFalse(stdout)


class TestIssue151(unittest.TestCase):
    """Multiple --no-show-* options can't be used together"""
    layer = Issues

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)

        # initialize repository
        self.repo = git.Repo.init(self.dirpath)
        self.repo.git.state(['extensions', 'create', 'log', '--command', 'git log'])
        self.repo.git.state(['extensions', 'create', 'stashes', '--command', 'git stash list'])

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test(self):
        """Issue 151: multiple --no-show options should work together"""

        # when
        state_proc = subprocess.Popen(
            'git state --no-color --no-show log --no-show stashes'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = [x.decode('utf-8') for x in state_proc.communicate()]

        # then
        self.assertRegexpMatches(stdout, '^# status.*')
        self.assertTrue('# log' not in stdout)
        self.assertTrue('# stashes' not in stdout)
        self.assertFalse(stderr)
