import os
import shutil
import subprocess
import tempfile
import unittest

import git

from . import testutils


class TestChanges(unittest.TestCase):

    def _output(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].strip()

    def test_changes_version(self):

        # expect
        self.assertRegexpMatches(self._output('git changes -v'.split()), 'git-changes \\d+\\.\\d+\\.\\d+')
        self.assertRegexpMatches(self._output('git changes --version'.split()), 'git-changes \\d+\\.\\d+\\.\\d+')

    def test_changes_help(self):

        # expect
        self.assertTrue(self._output('git changes -h'.split()))
        self.assertTrue(self._output('git changes --help'.split()))


class TestChangesView(unittest.TestCase):

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())

        # initial commit
        pyenv = os.environ.copy()
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-15T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-15T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'], env=pyenv)
        self.commit0_log = subprocess.check_output('git rev-parse --short HEAD'.split()).strip() + ' Initial commit'

        # edit readme
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-16T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-16T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-a', '-m', 'edit readme'], env=pyenv)
        self.commit1_log = subprocess.check_output('git rev-parse --short HEAD'.split()).strip() + ' edit readme'

        # add changelog
        subprocess.call('touch CHANGELOG.md'.split())
        subprocess.call('git add -A'.split())
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-17T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-17T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-m', 'add changelog'], env=pyenv)
        self.commit2_log = subprocess.check_output('git rev-parse --short HEAD'.split()).strip() + ' add changelog'

        # edit changelog
        with open('CHANGELOG.md', 'w') as a_file:
            a_file.write('changelog\n')
        pyenv['GIT_COMMITTER_DATE'] = '2016-02-18T00:00:00Z'
        pyenv['GIT_AUTHOR_DATE'] = '2016-02-18T00:00:00Z'
        subprocess.call(['git', 'commit', '--quiet', '-a', '-m', 'edit changelog'], env=pyenv)
        self.commit3_log = subprocess.check_output('git rev-parse --short HEAD'.split()).strip() + ' edit changelog'

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_view(self):

        # expect: no changes when there are none
        self.assertFalse(self.repo.git.changes())
        self.assertFalse(self.repo.git.changes('--log'))
        self.assertFalse(self.repo.git.changes('-l'))
        self.assertFalse(self.repo.git.changes('view'))
        self.assertFalse(self.repo.git.changes('view', '--log'))
        self.assertFalse(self.repo.git.changes('view', '-l'))

    def test_view_noAssociation_defaultOverridden(self):

        # given
        self.repo.git.config('git-changes.default-commit-ish', str(self.repo.rev_parse('HEAD^')))

        # expect
        self.assertEqual(self.commit3_log, self.repo.git.changes())
        self.assertEqual(self.commit3_log, self.repo.git.changes('--log'))
        self.assertEqual(self.commit3_log, self.repo.git.changes('-l'))
        self.assertEqual(self.commit3_log, self.repo.git.changes('view'))
        self.assertEqual(self.commit3_log, self.repo.git.changes('view', '--log'))
        self.assertEqual(self.commit3_log, self.repo.git.changes('view', '-l'))

    def test_view_withCommittish(self):

        # expect: changes when viewing with a commit-ish
        self.assertFalse(self.repo.git.changes('HEAD'))
        self.assertFalse(self.repo.git.changes('view', 'HEAD'))
        self.assertEqual(self.commit3_log, self.repo.git.changes('HEAD^'))
        self.assertEqual(self.commit3_log, self.repo.git.changes('view', 'HEAD^'))
        self.assertEqual(self.commit3_log, self.repo.git.changes('view', 'HEAD^', '--', '*md'))
        self.assertFalse(self.repo.git.changes('view', 'HEAD^', '--', '*py'))
        self.assertEqual(os.linesep.join([self.commit3_log, self.commit2_log]), self.repo.git.changes('HEAD^^'))
        self.assertEqual(os.linesep.join([self.commit3_log, self.commit2_log]), self.repo.git.changes('view', 'HEAD^^'))

    def test_view_upstream(self):

        # given: a local upstream branch
        self.repo.git.branch('upstream-branch', 'HEAD^')
        self.repo.git.branch('--set-upstream-to=upstream-branch')

        # given: an association
        self.repo.git.config('git-changes.associations.master.with', self.repo.rev_parse('HEAD^^'))

        # expect
        self.assertEqual(self.commit3_log, self.repo.git.changes('-u'))
        self.assertEqual(self.commit3_log, self.repo.git.changes('--upstream'))
        self.assertNotEqual(self.repo.git.changes(), self.repo.git.changes('--upstream'))

    def test_view_count(self):

        # expect:
        self.assertEqual('0', self.repo.git.changes('view', '-c'))
        self.assertEqual('0', self.repo.git.changes('view', '--count'))
        self.assertEqual('1', self.repo.git.changes('HEAD^', '-c'))
        self.assertEqual('1', self.repo.git.changes('view', 'HEAD^', '-c'))
        self.assertEqual('1', self.repo.git.changes('HEAD^', '--count'))
        self.assertEqual('1', self.repo.git.changes('view', 'HEAD^', '--count'))
        self.assertEqual('1', self.repo.git.changes('view', 'HEAD^', '--count', '--', '*md'))
        self.assertEqual('0', self.repo.git.changes('view', 'HEAD^', '--count', '--', '*py'))

    def test_view_stat(self):

        # expect:
        self.assertIn('1 insertion', self.repo.git.changes('HEAD^', '-s'))
        self.assertIn('1 insertion', self.repo.git.changes('view', 'HEAD^', '-s'))
        self.assertIn('1 insertion', self.repo.git.changes('HEAD^', '--stat'))
        self.assertIn('1 insertion', self.repo.git.changes('view', 'HEAD^', '--stat'))
        self.assertIn('1 insertion', self.repo.git.changes('view', 'HEAD^', '--stat', '--', '*md'))
        self.assertFalse(self.repo.git.changes('view', '--stat'))
        self.assertFalse(self.repo.git.changes('view', 'HEAD^', '--stat', '--', '*py'))

    def test_view_diff(self):

        # expect:
        self.assertIn('diff --git a/CHANGELOG.md b/CHANGELOG.md', self.repo.git.changes('HEAD^', '-d'))
        self.assertIn('diff --git a/CHANGELOG.md b/CHANGELOG.md', self.repo.git.changes('view', 'HEAD^', '-d'))
        self.assertIn('diff --git a/CHANGELOG.md b/CHANGELOG.md', self.repo.git.changes('HEAD^', '--diff'))
        self.assertIn('diff --git a/CHANGELOG.md b/CHANGELOG.md', self.repo.git.changes('view', 'HEAD^', '--diff'))
        self.assertIn('diff --git a/CHANGELOG.md b/CHANGELOG.md', self.repo.git.changes('view', 'HEAD^', '--diff', '--', '*md'))
        self.assertFalse(self.repo.git.changes('view', '--diff'))
        self.assertFalse(self.repo.git.changes('view', 'HEAD^', '--diff', '--', '*py'))

    def test_view_inverse(self):

        # given
        self.repo.git.config('git-changes.default-commit-ish', str(self.repo.rev_parse('HEAD^')))

        # expect
        expected = os.linesep.join([self.commit2_log, self.commit1_log, self.commit0_log])
        self.assertEqual(expected, self.repo.git.changes('view', '--inverse'))
        self.assertEqual(expected, self.repo.git.changes('view', '-i'))
        self.assertEqual(self.commit0_log, self.repo.git.changes('view', '-i', 'HEAD^^^'))

    def test_view_useAssociation_changesExist(self):

        # given
        self.repo.git.config('git-changes.associations.master.with', self.repo.rev_parse('HEAD^'))

        # expect
        self.assertEqual(self.commit3_log, self.repo.git.changes())
        self.assertEqual(self.commit3_log, self.repo.git.changes('view'))

    def test_view_useAssociation_noChangesExist(self):

        # given
        self.repo.git.config('git-changes.associations.master.with', self.repo.rev_parse('HEAD'))

        # expect
        self.assertFalse(self.repo.git.changes())
        self.assertFalse(self.repo.git.changes('view'))

    def test_view_overrideDefaultView(self):

        # given:
        self.repo.git.config('git-changes.default-view', 'count')

        # expect:
        self.assertEqual('0', self.repo.git.changes('view'))
        self.assertEqual('1', self.repo.git.changes('HEAD^', '-c'))


class TestChangesAssociate(unittest.TestCase):

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)

        # initial commit
        open('README.md', 'w').close()
        self.repo.index.add(['README.md'])
        self.repo.index.commit('Initial commit')

        # add changelog
        open('CHANGELOG.md', 'w').close()
        self.repo.index.add(['CHANGELOG.md'])
        self.repo.index.commit('Add changelog')

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_associate(self):

        # when
        output = self.repo.git.changes('associate', 'HEAD^')

        # then
        sha = str(self.repo.rev_parse('HEAD^'))
        self.assertEqual('master has been associated with {}'.format(sha), output)
        self.assertEqual(sha, self.repo.git.config('git-changes.associations.master.with'))

    def test_associate_quiet(self):

        # when
        output = self.repo.git.changes('associate', '--quiet', 'HEAD^')

        # then
        self.assertFalse(output)
        self.assertEqual(
            str(self.repo.rev_parse('HEAD^')),
            self.repo.git.config('git-changes.associations.master.with')
        )

    def test_associate_withUpstream(self):

        # given: a local upstream branch
        self.repo.git.branch('upstream-branch', 'HEAD^')
        self.repo.git.branch('--set-upstream-to=upstream-branch')

        # when
        output = self.repo.git.changes('associate', '--upstream')

        # then
        self.assertEqual('master has been associated with refs/heads/upstream-branch', output)
        self.assertEqual('refs/heads/upstream-branch', self.repo.git.config('git-changes.associations.master.with'))

    def test_associate_withUpstream_quiet(self):

        # given: a local upstream branch
        self.repo.git.branch('upstream-branch', 'HEAD^')
        self.repo.git.branch('--set-upstream-to=upstream-branch')

        # when
        output = self.repo.git.changes('associate', '--upstream', '--quiet')

        # then
        self.assertFalse(output)
        self.assertEqual('refs/heads/upstream-branch', self.repo.git.config('git-changes.associations.master.with'))

    def test_associate_get_emptyRepository(self):

        # given
        shutil.rmtree(self.dirpath)
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)

        # expect:
        self.assertEqual('warn: repository is empty', self.repo.git.changes('associate'))

    def test_associate_get_noAssociationExists_defaultUnspecified(self):

        # expect
        self.assertFalse(self.repo.git.changes('associate'))

    def test_associate_get_noAssociationExists_defaultUnspecified_verbose(self):

        # expect
        self.assertEqual('refs/heads/master', self.repo.git.changes('associate', '--verbose'))
        self.assertEqual('refs/heads/master', self.repo.git.changes('associate', '-V'))

    def test_associate_get_noAssociationExists_defaultOverridden(self):

        # given: overridden default commit-ish
        self.repo.git.config('--local', 'git-changes.default-commit-ish', self.repo.rev_parse('HEAD'))

        # expect
        self.assertFalse(self.repo.git.changes('associate'))

    def test_associate_get_noAssociationExists_defaultOverridden_verbose(self):

        # given: overridden default commit-ish
        self.repo.git.config('--local', 'git-changes.default-commit-ish', self.repo.rev_parse('HEAD'))

        # expect
        self.assertEqual(str(self.repo.rev_parse('HEAD')), self.repo.git.changes('associate', '--verbose'))
        self.assertEqual(str(self.repo.rev_parse('HEAD')), self.repo.git.changes('associate', '-V'))

    def test_associate_get_cannotBeUsedWithQuiet(self):

        # when
        output = subprocess.Popen(
            'git changes associate --quiet'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

        # then
        self.assertEqual('usage: git changes associate [-h] [-u] [-V] [COMMIT-ISH [-q]]\n', output[0])
        self.assertEqual('git changes: error: argument -q/--quiet: not allowed without positional argument committish '
                         'or option -u/--upstream\n', output[1])

    def test_associate_filesNotSupported(self):

        # when
        output = subprocess.Popen(
            'git changes associate -- file.txt'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

        # then
        self.assertEqual('usage: git changes associate [-h] [-u] [-V] [COMMIT-ISH [-q]]\n', output[0])
        self.assertEqual('git changes: error: argument FILES: only supported for view sub-command\n', output[1])


class TestChangesUnassociate(unittest.TestCase):

    def _output(self, command):
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return proc.communicate()[0].strip()

    def setUp(self):
        self.proj_dir = os.getcwd()
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        self.repo = git.Repo.init(self.dirpath)
        testutils.init_local_config(self.repo)
        subprocess.call('touch README.md'.split())
        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')
        subprocess.call('git add -A'.split())

        # initial commit
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])

        # edit readme
        with open('README.md', 'a') as a_file:
            a_file.write('readme\n')
        subprocess.call(['git', 'commit', '--quiet', '-a', '-m', 'edit readme'])

        # associate master
        head = self.repo.rev_parse('HEAD')
        self.repo.git.config('git-changes.associations.master.with', head)

        # associate a valid branch
        self.repo.git.branch('valid-branch')
        self.repo.git.config('git-changes.associations.valid-branch.with', head)

        # associate a non-existent branch
        self.repo.git.config('git-changes.associations.stale-branch.with', head)

    def tearDown(self):
        shutil.rmtree(self.dirpath)
        os.chdir(self.proj_dir)

    def test_unassociate_currentBranch(self):

        # when
        output = self.repo.git.changes('unassociate')

        # then
        self.assertFalse(output)
        self.assertFalse(self._output('git config git-changes.associations.master.with'.split()))
        self.assertTrue(self.repo.git.config('git-changes.associations.valid-branch.with'))
        self.assertTrue(self.repo.git.config('git-changes.associations.stale-branch.with'))

    def test_unassociate_all(self):

        # when
        output = self.repo.git.changes('unassociate', '--all')

        # then
        self.assertEqual("""Removed association 'master'
Removed association 'valid-branch'
Removed association 'stale-branch'""", output)
        self.assertFalse(self._output('git config git-changes.associations.master.with'.split()))
        self.assertFalse(self._output('git config git-changes.associations.valid-branch.with'.split()))
        self.assertFalse(self._output('git config git-changes.associations.stale-branch.with'.split()))

    def test_unassociate_prune(self):

        # when
        output = self.repo.git.changes('unassociate', '--prune')

        # then
        self.assertEqual("Removed association 'stale-branch'", output)
        self.assertTrue(self.repo.git.config('git-changes.associations.master.with'))
        self.assertTrue(self.repo.git.config('git-changes.associations.valid-branch.with'))
        self.assertFalse(self._output('git config git-changes.associations.stale-branch.with'.split()))

    def test_unassociate_quiet_currentBranch(self):

        # when
        output = self.repo.git.changes('unassociate', '--quiet')

        # then
        self.assertFalse(output)
        self.assertFalse(self._output('git config git-changes.associations.master.with'.split()))
        self.assertTrue(self.repo.git.config('git-changes.associations.valid-branch.with'))
        self.assertTrue(self.repo.git.config('git-changes.associations.stale-branch.with'))

    def test_unassociate_quiet_all(self):

        # when
        output = self.repo.git.changes('unassociate', '--quiet', '--all')

        # then
        self.assertFalse(output)
        self.assertFalse(self._output('git config git-changes.associations.master.with'.split()))
        self.assertFalse(self._output('git config git-changes.associations.valid-branch.with'.split()))
        self.assertFalse(self._output('git config git-changes.associations.stale-branch.with'.split()))

    def test_unassociate_quiet_prune(self):

        # when
        output = self.repo.git.changes('unassociate', '--quiet', '--prune')

        # then
        self.assertFalse(output)
        self.assertTrue(self.repo.git.config('git-changes.associations.master.with'))
        self.assertTrue(self.repo.git.config('git-changes.associations.valid-branch.with'))
        self.assertFalse(self._output('git config git-changes.associations.stale-branch.with'.split()))

    def test_unassociate_dryRun(self):

        # expect
        self.assertEqual(
            "Would unassociate 'master' from '{}'".format(self.repo.rev_parse('HEAD')),
            self.repo.git.changes('unassociate', '--dry-run')
        )
        self.assertEqual("""Would remove association 'master'
Would remove association 'valid-branch'
Would remove association 'stale-branch'""", self.repo.git.changes('unassociate', '--dry-run', '--all'))
        self.assertEqual(
            "Would remove association 'stale-branch'",
            self.repo.git.changes('unassociate', '--dry-run', '--prune')
        )

    def test_unassociate_dryRunDoesNotSupportQuiet(self):

        # when
        output = subprocess.Popen(
            'git changes unassociate --dry-run --quiet'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

        # then
        # TODO: usage should print to STDOUT
        self.assertFalse(output[0])
        self.assertEqual("""usage: git changes unassociate [-h] [-a | -p] [-q | -d]
git changes unassociate: error: argument -q/--quiet: not allowed with argument -d/--dry-run
""", output[1])

    def test_unassociate_filesNotSupported(self):

        # when
        output = subprocess.Popen(
            'git changes unassociate -- file.txt'.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).communicate()

        # then
        self.assertEqual('usage: git changes unassociate [-h] [-a | -p] [-q | -d]\n', output[0])
        self.assertEqual('git changes: error: argument FILES: only supported for view sub-command\n', output[1])
