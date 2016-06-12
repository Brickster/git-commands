import os
import shutil
import subprocess
import tempfile
import unittest


class TestGitUpstream(unittest.TestCase):

    def setUp(self):
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        subprocess.call('git init --quiet'.split())
        subprocess.call('touch README.md'.split())
        subprocess.call('git add -A'.split())
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])
        subprocess.call('git checkout -b develop --quiet'.split())
        subprocess.call('git branch --set-upstream-to=master --quiet'.split())

    def tearDown(self):
        shutil.rmtree(self.dirpath)

    def test_upstream(self):
        self.assertEqual('master', subprocess.check_output('git upstream'.split()).strip())

    def test_upstream_includeRemote_shortOption(self):
        self.assertEqual('./master', subprocess.check_output('git upstream -r'.split()).strip())

    def test_upstream_includeRemote_longOption(self):
        self.assertEqual('./master', subprocess.check_output('git upstream --include-remote'.split()).strip())

    def test_upstream_excludeRemote_shortOption(self):
        self.assertEqual('master', subprocess.check_output('git upstream -R'.split()).strip())

    def test_upstream_excludeRemote_longOption(self):
        self.assertEqual('master', subprocess.check_output('git upstream --no-include-remote'.split()).strip())

    def test_upstream_showRemotePropertyTrue(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote true'.split())

        # run
        upstream_result = subprocess.check_output('git upstream'.split()).strip()

        # verify
        self.assertEqual('./master', upstream_result)

    def test_upstream_showRemotePropertyTrue_includeRemote_shortOption(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote true'.split())

        # run
        upstream_result = subprocess.check_output('git upstream -r'.split()).strip()

        # verify
        self.assertEqual('./master', upstream_result)

    def test_upstream_showRemotePropertyTrue_includeRemote_longOption(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote true'.split())

        # run
        upstream_result = subprocess.check_output('git upstream --include-remote'.split()).strip()

        # verify
        self.assertEqual('./master', upstream_result)

    def test_upstream_showRemotePropertyTrue_excudeRemote_shortOption(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote true'.split())

        # run
        upstream_result = subprocess.check_output('git upstream -R'.split()).strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_showRemotePropertyTrue_excudeRemote_longOption(self):

        # setup
        subprocess.call('git config --local git-upstream.include-remote true'.split())

        # run
        upstream_result = subprocess.check_output('git upstream --no-include-remote'.split()).strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_specifyBranch_shortOption(self):

        # setup
        subprocess.call('git checkout -b new-feature --quiet'.split())

        # run
        upstream_result = subprocess.check_output('git upstream -b develop'.split()).strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_specifyBranch_longOption(self):

        # setup
        subprocess.call('git checkout -b new-feature --quiet'.split())

        # run
        upstream_result = subprocess.check_output('git upstream --branch develop'.split()).strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_specifyBranch_longOptionEqual(self):

        # setup
        subprocess.call('git checkout -b new-feature --quiet'.split())

        # run
        upstream_result = subprocess.check_output('git upstream --branch=develop'.split()).strip()

        # verify
        self.assertEqual('master', upstream_result)

    def test_upstream_noUpstream(self):

        # setup
        subprocess.call('git branch --unset-upstream'.split())

        # run
        upstream_result = subprocess.check_output('git upstream'.split())

        # verify
        self.assertFalse(upstream_result)

    def test_upstream_invalidBranch(self):

        # setup
        branch = 'invalidbranch'

        # run
        p = subprocess.Popen(['git', 'upstream', '-b', branch], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # verify
        self.assertEqual('error: {0!r} is not a valid branch'.format(branch), stderr.strip())
        self.assertFalse(stdout)

    def test_upstream_nonGitRepository(self):

        # setup
        os.mkdir(self.dirpath + '/dir')
        os.chdir(self.dirpath + '/dir')

        # run
        p = subprocess.Popen('git upstream'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # verify
        expected = "error: '{}' not a git repository".format('/private' + self.dirpath + '/dir')
        self.assertEqual(expected, stderr.strip())
        self.assertFalse(stdout)
