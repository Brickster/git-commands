import mock
import subprocess
import unittest

import testutils
from bin.commands import changes, upstream


class TestChangesAssociate(unittest.TestCase):

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_detached', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous', return_value=False)
    @mock.patch('bin.commands.utils.git.symbolic_full_name')
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_associate_isRef_notAmbiguous(
            self,
            mock_info,
            mock_call,
            mock_currentbranch,
            mock_symbolicfullname,
            mock_isrefambiguous,
            mock_isref,
            mock_isdetached,
            mock_isgitrepository
    ):

        # setup
        cur_branch = 'cur-branch'
        mock_currentbranch.return_value = cur_branch
        fullname = 'fullname'
        mock_symbolicfullname.return_value = fullname

        # when
        committish = 'c123'
        quiet = True
        changes.associate(committish, quiet=quiet)

        # then
        mock_isgitrepository.assert_called_once()
        mock_isdetached.assert_called_once()
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_called_once_with(committish, limit=('heads', 'tags'))
        mock_symbolicfullname.assert_called_once_with(committish)
        mock_currentbranch.assert_called_once()
        mock_call.assert_called_once_with(
            ['git', 'config', '--local', 'git-changes.associations.' + cur_branch + '.with', fullname]
        )
        mock_info.assert_called_once_with('{} has been associated with {}'.format(cur_branch, fullname), quiet)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_detached', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous', return_value=True)
    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_associate_isRef_isAmbiguous(
            self,
            mock_error,
            mock_checkoutput,
            mock_isrefambiguous,
            mock_isref,
            mock_isdetached,
            mock_isgitrepository
    ):

        # given
        committish = 'abc123'
        ref_names = ['refs/heads/master', 'refs/tags/master']
        refs = '\n'.join(['84f9c10be201690f30252c0c6ef1504fad68251d ' + r for r in ref_names]) + '\n'
        mock_checkoutput.return_value = refs

        # when
        try:
            changes.associate(committish, quiet=False)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once()
        mock_isdetached.assert_called_once()
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_called_once_with(committish, limit=('heads', 'tags'))
        mock_checkoutput.assert_called_once_with(('git', 'show-ref', '--tags', '--heads', committish))
        mock_error.assert_called_once_with(
            '{0!r} is an ambiguous ref. Use one of:\n{1}'.format(committish, '\n'.join(ref_names))
        )

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_detached', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_sha1')
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_associate_notARef(
            self,
            mock_info,
            mock_call,
            mock_currentbranch,
            mock_resolvesha1,
            mock_isref,
            mock_isdetached,
            mock_isgitrepository
    ):

        # setup
        cur_branch = 'cur-branch'
        mock_currentbranch.return_value = cur_branch
        resolved_sha1 = 'sha123'
        mock_resolvesha1.return_value = resolved_sha1

        # when
        committish = 'c123'
        quiet = True
        changes.associate(committish, quiet=quiet)

        # then
        mock_isgitrepository.assert_called_once()
        mock_isdetached.assert_called_once()
        mock_isref.assert_called_once_with(committish)
        mock_resolvesha1.assert_called_once_with(committish)
        mock_currentbranch.assert_called_once()
        mock_call.assert_called_once_with(
            ['git', 'config', '--local', 'git-changes.associations.' + cur_branch + '.with', resolved_sha1]
        )
        mock_info.assert_called_once_with('{} has been associated with {}'.format(cur_branch, resolved_sha1), quiet)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_detached', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_sha1', return_value=None)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_associate_notARef_invalidRevision(
            self,
            mock_error,
            mock_resolvesha1,
            mock_isref,
            mock_isdetached,
            mock_isgitrepository
    ):

        # when
        committish = 'c123'
        quiet = True
        try:
            changes.associate(committish, quiet=quiet)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once()
        mock_isdetached.assert_called_once()
        mock_isref.assert_called_once_with(committish)
        mock_resolvesha1.assert_called_once_with(committish)
        mock_error.assert_called_once_with('{} is not a valid revision'.format(committish))

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test_associate_notagitrepository(self, mock_getcwd, mock_error, mock_isgitrepository):

        # when
        try:
            changes.associate('HEAD')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_error.assert_called_once_with("'/working/dir' not a git repository")
        mock_getcwd.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_detached', return_value=True)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_associate_isDetached(self, mock_error, mock_isdetached, mock_isgitrepository):

        # when
        try:
            changes.associate('abc123')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once()
        mock_error.assert_called_once_with('cannot associate while HEAD is detached')


class TestChangesAssociateUpstream(unittest.TestCase):

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.upstream.upstream')
    @mock.patch('bin.commands.changes.associate')
    def test_associate_upstream(self, mock_associate, mock_upstream, mock_currentbranch, mock_isgitrepository):

        # given
        current_branch = 'cur-branch'
        upstream_branch = 'upstream-branch'
        quiet = True
        mock_currentbranch.return_value = current_branch
        mock_upstream.return_value = upstream_branch

        # when
        changes.associate_upstream(quiet)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()
        mock_upstream.assert_called_once_with(current_branch, include_remote=upstream.IncludeRemote.ALWAYS)
        mock_associate.assert_called_once_with(upstream_branch, quiet)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.upstream.upstream')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_associate_upstream_noupstream(self, mock_error, mock_upstream, mock_currentbranch, mock_isgitrepository):

        # given
        branch = 'cur-branch'
        mock_currentbranch.return_value = branch
        mock_upstream.return_value = ''

        # when
        try:
            changes.associate_upstream()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_error.assert_called_once_with('{} has no upstream branch'.format(branch))

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test_associate_upstream_notagitrepository(self, mock_getcwd, mock_error, mock_isgitrepository):

        # when
        try:
            changes.associate_upstream()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_error.assert_called_once_with("'/working/dir' not a git repository")
        mock_getcwd.assert_called_once_with()


class TestChangesGetAssociatedBranches(unittest.TestCase):

    @mock.patch('subprocess.Popen')
    def test_getAssociatedBranches(self, mock_popen):

        # given
        association_keys = """git-changes.associations.develop.with
git-changes.associations.master.with
"""

        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [association_keys, None]
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        # when
        actual_associations = changes._get_associated_branches()

        # then
        self.assertEqual(actual_associations, ['develop', 'master'])
        mock_popen.assert_called_once_with(
            ('git', 'config', '--local', '--name-only', '--get-regexp', 'git-changes.associations'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        mock_proc.communicate.assert_called_once()


class TestChangesPruneAssociations(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._unassociate = changes.unassociate
        self._get_associated_branches = changes._get_associated_branches

    def tearDown(self):
        changes.unassociate = self._unassociate
        changes._get_associated_branches = self._get_associated_branches

    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.changes._get_associated_branches')
    @mock.patch('bin.commands.changes.unassociate')
    @mock.patch('bin.commands.utils.messages.info')
    def test_prune_associations(self, mock_info, mock_unassociate, mock_getassociatedbranches, mock_checkoutput, mock_isemptyrepository):

        # setup
        refs = "84f9c10be201690f30252c0c6ef1504fad68251d refs/heads/master\n"
        association_keys = ['develop', 'master']
        mock_checkoutput.return_value = refs
        mock_getassociatedbranches.return_value = association_keys

        # when
        quiet = True
        changes._prune_associations('prune', quiet=quiet)

        # then
        mock_isemptyrepository.assert_called_once()
        mock_checkoutput.assert_called_once_with(('git', 'show-ref', '--heads'))
        mock_getassociatedbranches.assert_called_once()
        mock_unassociate.assert_called_once_with('develop')
        mock_info.assert_called_once_with("Removed association 'develop'", quiet)

    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.changes._get_associated_branches')
    @mock.patch('bin.commands.changes.unassociate')
    @mock.patch('bin.commands.utils.messages.info')
    def test_prune_associations_dryRun(self, mock_info, mock_unassociate, mock_getassociatedbranches, mock_checkoutput, mock_isemptyrepository):

        # setup
        refs = "84f9c10be201690f30252c0c6ef1504fad68251d refs/heads/master\n"
        association_keys = ['develop', 'master']
        mock_checkoutput.return_value = refs
        mock_getassociatedbranches.return_value = association_keys

        # when
        quiet = True
        changes._prune_associations('prune', quiet=quiet, dry_run=True)

        # then
        mock_isemptyrepository.assert_called_once()
        mock_checkoutput.assert_called_once_with(('git', 'show-ref', '--heads'))
        mock_getassociatedbranches.assert_called_once()
        mock_unassociate.assert_not_called()
        mock_info.assert_called_once_with("Would remove association 'develop'", quiet)

    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.changes._get_associated_branches')
    @mock.patch('bin.commands.changes.unassociate')
    @mock.patch('bin.commands.utils.messages.info')
    def test_prune_associations_all(self, mock_info, mock_unassociate, mock_getassociatedbranches, mock_checkoutput, mock_isemptyrepository):

        # setup
        refs = """84f9c10be201690f30252c0c6ef1504fad68251d refs/heads/develop
84f9c10be201690f30252c0c6ef1504fad68251d refs/heads/master
"""
        association_keys = ['develop', 'master']
        mock_checkoutput.return_value = refs
        mock_getassociatedbranches.return_value = association_keys

        # when
        quiet = True
        changes._prune_associations('all', quiet=quiet)

        # then
        mock_isemptyrepository.assert_called_once()
        mock_checkoutput.assert_called_once_with(('git', 'show-ref', '--heads'))
        mock_getassociatedbranches.assert_called_once()
        mock_unassociate.assert_has_calls([
            mock.call('develop'),
            mock.call('master')
        ])
        mock_info.assert_has_calls([
            mock.call("Removed association 'develop'", quiet),
            mock.call("Removed association 'master'", quiet)
        ])

    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=True)
    def test_pruneAssociations_newRepository(self, mock_isemptyrepository):

        # when
        changes._prune_associations(None, None)

        # then
        mock_isemptyrepository.assert_called_once()


class TestChangesUnassociate(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._get_association = changes.get_association

    def tearDown(self):
        changes.get_association = self._get_association

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.changes.get_association')
    @mock.patch('subprocess.call')
    def test_unassociate_branch(self, mock_call, mock_getassociation, mock_currentbranch, mock_isgitrepository):

        # given
        branch = 'the-branch'
        mock_getassociation.return_value = branch

        # when
        changes.unassociate(branch=branch)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_getassociation.assert_called_once_with(branch)
        mock_call.assert_called_once_with(
            ['git', 'config', '--local', '--remove-section', 'git-changes.associations.' + branch]
        )

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.changes.get_association')
    def test_unassociate_branch_dryRun(self, mock_getassociation, mock_info, mock_call, mock_currentbranch, mock_isgitrepository):

        # given
        associated_branch = 'associated-branch'
        mock_getassociation.return_value = associated_branch

        # when
        branch = 'the-branch'
        changes.unassociate(branch=branch, dry_run=True)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_call.assert_not_called()
        mock_info.assert_called_once_with('Would unassociate {0!r} from {1!r}'.format(branch, associated_branch))
        mock_getassociation.assert_called_once()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('subprocess.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.changes.get_association')
    def test_unassociate_branch_dryRun_noExistingAssociation(
            self,
            mock_getassociation,
            mock_info,
            mock_call,
            mock_currentbranch,
            mock_isgitrepository
    ):

        # given
        associated_branch = None
        mock_getassociation.return_value = associated_branch

        # when
        branch = 'the-branch'
        changes.unassociate(branch=branch, dry_run=True)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_call.assert_not_called()
        mock_info.assert_not_called()
        mock_getassociation.assert_called_once()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.changes.get_association')
    @mock.patch('subprocess.call')
    def test_unassociate_nobranch(self, mock_call, mock_getassociation, mock_currentbranch, mock_isgitrepository):

        # setup
        current_branch = 'the-current'
        mock_currentbranch.return_value = current_branch
        mock_getassociation.return_value = current_branch

        # when
        changes.unassociate()

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()
        mock_getassociation.assert_called_once_with(current_branch)
        mock_call.assert_called_once_with(
            ['git', 'config', '--local', '--remove-section', 'git-changes.associations.' + current_branch]
        )

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test_unassociate_notagitrepository(self, mock_getcwd, mock_error, mock_isgitrepository):

        # when
        try:
            changes.unassociate()
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_error.assert_called_once_with("'/working/dir' not a git repository")
        mock_getcwd.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.changes._prune_associations')
    def test_unassociate_cleanup(self, mock_pruneassociations, mock_isgitrepository):

        # when
        quiet = True
        cleanup = 'all'
        dry_run = True
        changes.unassociate(cleanup=cleanup, quiet=quiet, dry_run=dry_run)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_pruneassociations.assert_called_once_with(cleanup, quiet, dry_run)

    def test_unassociate_cleanup_invalidtype(self):

        # when
        try:
            changes.unassociate(cleanup='notvalid')
            self.fail('expected AssertionError but found none')  # pragma: no cover
        except AssertionError as error:
            # then
            self.assertEqual(error.message, 'cleanup must be one of ' + str(['all', 'prune']))

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.changes.get_association')
    @mock.patch('subprocess.call')
    def test_unassociate_noAssociation(self, mock_call, mock_getassociation, mock_currentbranch, mock_isgitrepository):

        # given
        branch = 'the-branch'
        mock_getassociation.return_value = None

        # when
        changes.unassociate(branch=branch)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_getassociation.assert_called_once_with(branch)
        mock_call.assert_not_called()


class TestChangesGetAssociation(unittest.TestCase):

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.settings.get')
    def test_getassociation(self, mock_get, mock_currentbranch, mock_isgitrepository):

        # setup
        expected_association = 'the-association'
        mock_get.return_value = expected_association

        # when
        branch = 'the-branch'
        actual_association = changes.get_association(branch)

        # then
        self.assertEqual(actual_association, expected_association)
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_get.assert_called_once_with('git-changes.associations.' + branch + '.with', config='local')

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.settings.get')
    def test_getassociation_nobranch(self, mock_get, mock_currentbranch, mock_isgitrepository):

        # setup
        expected_association = 'the-association'
        mock_get.return_value = expected_association
        current_branch = 'cur-branch'
        mock_currentbranch.return_value = current_branch

        # when
        actual_association = changes.get_association()

        # then
        self.assertEqual(actual_association, expected_association)
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()
        mock_get.assert_called_once_with('git-changes.associations.' + current_branch + '.with', config='local')

    # the branch will be none for empty repositories
    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch', return_value = None)
    def test_getassociation_nobranch_none(self, mock_currentbranch, mock_isgitrepository):

        # setup
        mock_currentbranch.return_value = None

        # when
        actual_association = changes.get_association()

        # then
        self.assertFalse(actual_association)
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test_getassociation_notagitrepository(self, mock_getcwd, mock_error, mock_isgitrepository):

        # when
        try:
            changes.get_association('HEAD')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_error.assert_called_once_with("'/working/dir' not a git repository")
        mock_getcwd.assert_called_once_with()


class TestChangesChanges(unittest.TestCase):

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous')
    @mock.patch('bin.commands.settings.get')
    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.call')
    def test_changes_isnotref(
            self,
            mock_call,
            mock_checkoutput,
            mock_get,
            mock_isrefambiguous,
            mock_isref,
            mock_iscommit,
            mock_isgitrepository
    ):

        # when
        committish = 'commit-ish'
        color_when = 'never'
        changes.changes(committish, color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_not_called()
        mock_get.assert_not_called()
        mock_call.assert_called_once_with(
            ['git', 'log', '--oneline', '{}..HEAD'.format(committish), '--color=' + color_when]
        )
        mock_checkoutput.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous', return_value=False)
    @mock.patch('bin.commands.settings.get')
    @mock.patch('subprocess.check_output')
    @mock.patch('subprocess.call')
    def test_changes_isref(
            self,
            mock_call,
            mock_checkoutput,
            mock_get,
            mock_isrefambiguous,
            mock_isref,
            mock_iscommit,
            mock_isgitrepository
    ):

        # when
        committish = 'commit-ish'
        color_when = 'never'
        changes.changes(committish, color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_called_once_with(committish, limit=('heads', 'tags'))
        mock_get.assert_not_called()
        mock_call.assert_called_once_with(
            ['git', 'log', '--oneline', '{}..HEAD'.format(committish), '--color=' + color_when]
        )
        mock_checkoutput.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='/working/dir')
    def test_changes_notagitrepository(self, mock_getcwd, mock_error, mock_isgitrepository):

        # when
        try:
            changes.changes('HEAD')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_error.assert_called_once_with("'/working/dir' not a git repository")
        mock_getcwd.assert_called_once_with()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_changes_notacommit(self, mock_error, mock_iscommit, mock_isgitrepository):

        # when
        committish = 'commit-ish'
        try:
            changes.changes(committish)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_error.assert_called_once_with('{0!r} is not a valid commit'.format(committish))

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous', return_value=True)
    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_changes_isrefandisambiguous(
            self, mock_error, mock_checkoutput, mock_isrefambiguous, mock_isref, mock_iscommit, mock_isgitrepository
    ):
        # setup
        ref_names = ['refs/heads/master', 'refs/tags/mtag']
        refs = '\n'.join(['84f9c10be201690f30252c0c6ef1504fad68251d ' + r for r in ref_names]) + '\n'
        mock_checkoutput.return_value = refs

        # when
        committish = 'commit-ish'
        try:
            changes.changes(committish)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_called_once_with(committish, limit=('heads', 'tags'))
        mock_checkoutput.assert_called_once_with(('git', 'show-ref', '--tags', '--heads', committish))
        mock_error.assert_called_once_with(
            '{0!r} is an ambiguous ref. Use one of:\n{1}'.format(committish, '\n'.join(ref_names))
        )

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.settings.get')
    @mock.patch('sys.stdout.isatty')
    @mock.patch('subprocess.call')
    def test_changes_color_never(
            self, mock_call, mock_isatty, mock_get, mock_isref, mock_iscommit, mock_isgitrepository
    ):

        # when
        color_when = 'never'
        changes.changes('HEAD', color_when=color_when)

        # then
        mock_get.assert_not_called()
        mock_isatty.assert_not_called()
        mock_call.assert_called_once_with(['git', 'log', '--oneline', 'HEAD..HEAD', '--color=' + color_when])

    def test_changes_color_invalidcolor(self):

        # when
        try:
            changes.changes('HEAD', color_when='invalid')
            self.fail('expected AssertionError but found none')  # pragma: no cover
        except AssertionError as error:
            # then
            self.assertEqual(error.message, 'color_when must be one of ' + str(('always', 'auto', 'never')))

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.settings.get', return_value='always')
    @mock.patch('subprocess.call')
    def test_changes_color_nonespecified(self, mock_call, mock_get, mock_isref, mock_iscommit, mock_isgetrepository):

        # when
        changes.changes('HEAD', color_when=None)

        # then
        mock_get.assert_called_once_with('color.ui', default='auto')
        mock_call.assert_called_once_with(['git', 'log', '--oneline', 'HEAD..HEAD', '--color=always'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.settings.get')
    @mock.patch('sys.stdout.isatty', return_value=False)
    @mock.patch('subprocess.call')
    def test_changes_color_auto_notatty(
            self, mock_call, mock_isatty, mock_get, mock_isref, mock_iscommit, mock_isgitrepository
    ):

        # when
        color_when = 'auto'
        changes.changes('HEAD', color_when=color_when)

        # then
        mock_get.assert_not_called()
        mock_isatty.assert_called_once_with()
        mock_call.assert_called_once_with('git log --oneline HEAD..HEAD --color=never'.split())

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.settings.get')
    @mock.patch('sys.stdout.isatty', return_value=True)
    @mock.patch('subprocess.call')
    def test_changes_color_auto_isatty(
            self, mock_call, mock_isatty, mock_get, mock_isref, mock_iscommit, mock_isgitrepository
    ):

        # when
        color_when = 'auto'
        changes.changes('HEAD', color_when=color_when)

        # then
        mock_get.assert_not_called()
        mock_isatty.assert_has_calls([mock.call(), mock.call()])
        mock_call.assert_called_once_with('git log --oneline HEAD..HEAD --color=always'.split())

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('subprocess.call')
    def test_changes_details_diff(self, mock_call, mock_isref, mock_iscommit, mock_isgitrepository):

        # when
        committish = 'commit-ish'
        color_when = 'never'
        changes.changes(committish, details='diff', color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_call.assert_called_once_with(['git', 'diff', '--color={}'.format(color_when), committish + '...HEAD'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('subprocess.call')
    def test_changes_details_stat(self, mock_call, mock_isref, mock_iscommit, mock_isgitrepository):

        # when
        committish = 'commit-ish'
        color_when = 'never'
        changes.changes(committish, details='stat', color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_call.assert_called_once_with(
            ['git', 'diff', '--color={}'.format(color_when), '--stat', committish + '...HEAD']
        )

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('subprocess.check_output')
    @mock.patch('bin.commands.utils.messages.info')
    def test_changes_details_count(self, mock_info, mock_checkoutput, mock_isref, mock_iscommit, mock_isgitrepository):

        # setup
        log = ['one', 'two', 'three']
        mock_checkoutput.return_value = '\n'.join(log) + '\n'

        # when
        committish = 'commit-ish'
        color_when = 'never'
        changes.changes(committish, details='count', color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_checkoutput.assert_called_once_with(['git', 'log', '--oneline', '{}..HEAD'.format(committish)])
        mock_info.assert_called_once_with(str(len(log)))

    def test_changes_details_invalidoption(self):

        # when
        try:
            changes.changes('HEAD', details='invalid')
            self.fail('expected AssertionError but found none')  # pragma: no cover
        except AssertionError as error:
            # then
            self.assertEqual(error.message, 'details must be one of ' + str(('diff', 'stat', 'count')))
