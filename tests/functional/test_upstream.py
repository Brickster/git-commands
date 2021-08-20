import os
import shutil
import subprocess
import tempfile
import unittest

import git

from . import testutils
from ..layers import GitUpstreamFunctional


class TestGitUpstream(unittest.TestCase):
    layer = GitUpstreamFunctional

    def _output(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].decode('utf-8').strip()

    def setUp(self):
        self.proj_dir = os.getcwd()

        # init repo
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)

        subprocess.call('touch README.md'.split())
        subprocess.call('git add -A'.split())
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])
        subprocess.call('git checkout -b develop --quiet'.split())
        subprocess.call('git branch --set-upstream-to=master --quiet'.split())

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_upstream(self):
        self.assertEqual('master', subprocess.check_output('git upstream'.split()).decode('utf-8').strip())

    def test_upstream_includeRemote_shortOption(self):
        self.assertEqual('./master', subprocess.check_output('git upstream -r'.split()).decode('utf-8').strip())

    def test_upstream_includeRemote_longOption(self):
        self.assertEqual('./master', subprocess.check_output('git upstream --include-remote'.split()).decode('utf-8').strip())

    def test_upstream_excludeRemote_shortOption(self):
        self.assertEqual('master', subprocess.check_output('git upstream -R'.split()).decode('utf-8').strip())

    def test_upstream_excludeRemote_longOption(self):
        self.assertEqual('master', subprocess.check_output('git upstream --no-include-remote'.split()).decode('utf-8').strip())

    def test_upstream_showRemoteProperty_never(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote NEVER'.split())

        # run
        upstream_result = subprocess.check_output('git upstream'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_showRemoteProperty_always(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote ALWAYS'.split())

        # run
        upstream_result = subprocess.check_output('git upstream'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('./master', upstream_result)

    def test_upstream_showRemoteProperty_noneLocal_isLocal(self):

        # setup
        subprocess.call('git config --local branch.develop.remote origin'.split())
        subprocess.call('git config --local git-upstream.include-remote NONE_LOCAL'.split())

        # run
        upstream_result = subprocess.check_output('git upstream'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('origin/master', upstream_result)

    def test_upstream_showRemoteProperty_noneLocal_notLocal(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote NONE_LOCAL'.split())

        # run
        upstream_result = subprocess.check_output('git upstream'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_ignoreShowRemotePropertyWithFlag_includeRemote_shortOption(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote NEVER'.split())

        # run
        upstream_result = subprocess.check_output('git upstream -r'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('./master', upstream_result)

    def test_upstream_ignoreShowRemotePropertyWithFlag_includeRemote_longOption(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote NEVER'.split())

        # run
        upstream_result = subprocess.check_output('git upstream --include-remote'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('./master', upstream_result)

    def test_upstream_ignoreShowRemotePropertyWithFlag_excudeRemote_shortOption(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote ALWAYS'.split())

        # run
        upstream_result = subprocess.check_output('git upstream -R'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_ignoreShowRemotePropertyWithFlag_excudeRemote_longOption(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote ALWAYS'.split())

        # run
        upstream_result = subprocess.check_output('git upstream --no-include-remote'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_specifyBranch_shortOption(self):

        # setup
        subprocess.call('git checkout -b new-feature --quiet'.split())

        # run
        upstream_result = subprocess.check_output('git upstream -b develop'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_specifyBranch_longOption(self):

        # setup
        subprocess.call('git checkout -b new-feature --quiet'.split())

        # run
        upstream_result = subprocess.check_output('git upstream --branch develop'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_specifyBranch_longOptionEqual(self):

        # setup
        subprocess.call('git checkout -b new-feature --quiet'.split())

        # run
        upstream_result = subprocess.check_output('git upstream --branch=develop'.split()).decode('utf-8').strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_noUpstream(self):

        # setup
        subprocess.call('git branch --unset-upstream'.split())

        # run
        upstream_result = subprocess.check_output('git upstream'.split()).decode('utf-8')

        # verify
        self.assertFalse(upstream_result)

    def test_upstream_invalidBranch(self):

        # setup
        branch = 'invalidbranch'

        # run
        p = subprocess.Popen(['git', 'upstream', '-b', branch], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = [x.decode('utf-8') for x in p.communicate()]

        # verify
        self.assertEqual('error: {0!r} is not a valid branch'.format(branch), stderr.strip())
        self.assertFalse(stdout)

    def test_upstream_nonGitRepository(self):

        # setup
        os.mkdir(self.dirpath + '/dir')
        os.chdir(self.dirpath + '/dir')

        # run
        p = subprocess.Popen('git upstream'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = [x.decode('utf-8') for x in p.communicate()]

        # verify
        expected = "error: '{}' not a git repository".format(os.path.realpath(self.dirpath) + '/dir')
        self.assertEqual(expected, stderr.strip())
        self.assertFalse(stdout)

    def test_upstream_emptyRepository(self):

        # setup
        # create a new repo in a sub-directory (lazy)
        os.mkdir(self.dirpath + '/dir')
        os.chdir(self.dirpath + '/dir')
        subprocess.check_output('git init -b main'.split())

        # when
        p = subprocess.Popen('git upstream'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = [x.decode('utf-8') for x in p.communicate()]

        # then
        self.assertFalse(stdout)
        self.assertFalse(stderr)

    def test_upstream_includeRemoteAndNoIncludeRemote(self):

        expected = """usage: git upstream [-h] [-v] [-r | -R] [-b BRANCH]
git upstream: error: argument -R/--no-include-remote: not allowed with argument -r/--include-remote
"""

        # run 1
        stdout, stderr = [x.decode('utf-8') for x in subprocess.Popen('git upstream --include-remote --no-include-remote'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()]
        self.assertFalse(stdout)
        self.assertEqual(stderr, expected)

        # run 2
        stdout, stderr = [x.decode('utf-8') for x in subprocess.Popen('git upstream --include-remote -R'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()]
        self.assertFalse(stdout)
        self.assertEqual(stderr, expected)

        # run 3
        stdout, stderr = [x.decode('utf-8') for x in subprocess.Popen('git upstream -r --no-include-remote'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()]
        self.assertFalse(stdout)
        self.assertEqual(stderr, expected)

        # run 4
        stdout, stderr = [x.decode('utf-8') for x in subprocess.Popen('git upstream -r -R'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()]
        self.assertFalse(stdout)
        self.assertEqual(stderr, expected)

    def test_upstream_version(self):

        # expect
        self.assertRegexpMatches(self._output('git upstream -v'.split()), 'git-upstream \\d+\\.\\d+\\.\\d+')
        self.assertRegexpMatches(self._output('git upstream --version'.split()), 'git-upstream \\d+\\.\\d+\\.\\d+')

    def test_upstream_help(self):

        # expect
        self.assertTrue(self._output('git upstream -h'.split()))
        self.assertTrue(self._output('git upstream --help'.split()))
