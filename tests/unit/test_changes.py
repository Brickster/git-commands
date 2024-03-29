import mock
import unittest

from . import testutils
from ..layers import GitChanges
from bin.commands import changes, upstream
from bin.commands.utils import git


class TestChangesAssociate(unittest.TestCase):
    layer = GitChanges

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.is_detached', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous', return_value=False)
    @mock.patch('bin.commands.utils.git.symbolic_full_name')
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.utils.execute.call')
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
            mock_isemptyrepository,
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
        mock_isemptyrepository.assert_called_once_with()
        mock_isdetached.assert_called_once()
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_called_once_with(committish, limit=(git.RefType.HEADS, git.RefType.TAGS))
        mock_symbolicfullname.assert_called_once_with(committish)
        mock_currentbranch.assert_called_once()
        mock_call.assert_called_once_with(
            ['git', 'config', '--local', 'git-changes.associations.' + cur_branch + '.with', fullname]
        )
        mock_info.assert_called_once_with('{} has been associated with {}'.format(cur_branch, fullname), quiet)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.is_detached', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_associate_isRef_isAmbiguous(
            self,
            mock_error,
            mock_checkoutput,
            mock_isrefambiguous,
            mock_isref,
            mock_isdetached,
            mock_isemptyrepository,
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
        mock_isemptyrepository.assert_called_once_with()
        mock_isdetached.assert_called_once_with()
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_called_once_with(committish, limit=(git.RefType.HEADS, git.RefType.TAGS))
        mock_checkoutput.assert_called_once_with(['git', 'show-ref', '--tags', '--heads', committish])
        mock_error.assert_called_once_with(
            '{0!r} is an ambiguous ref. Use one of:\n{1}'.format(committish, '\n'.join(ref_names))
        )

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.is_detached', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_sha1')
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    def test_associate_notARef(
            self,
            mock_info,
            mock_call,
            mock_currentbranch,
            mock_resolvesha1,
            mock_isref,
            mock_isdetached,
            mock_isemptyrepository,
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
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_isdetached.assert_called_once_with()
        mock_isref.assert_called_once_with(committish)
        mock_resolvesha1.assert_called_once_with(committish)
        mock_currentbranch.assert_called_once()
        mock_call.assert_called_once_with(
            ['git', 'config', '--local', 'git-changes.associations.' + cur_branch + '.with', resolved_sha1]
        )
        mock_info.assert_called_once_with('{} has been associated with {}'.format(cur_branch, resolved_sha1), quiet)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
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
            mock_isemptyrepository,
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
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_isdetached.assert_called_once_with()
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
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=True)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_associate_repositoryisempty(self, mock_error, mock_isemptyrepository, mock_isgitrepository):

        # when
        try:
            changes.associate('HEAD')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_error.assert_called_once_with('cannot associate while empty')

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.is_detached', return_value=True)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_associate_isDetached(self, mock_error, mock_isdetached, mock_isemptyrepository, mock_isgitrepository):

        # when
        try:
            changes.associate('abc123')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_isdetached.assert_called_once_with()
        mock_error.assert_called_once_with('cannot associate while HEAD is detached')


class TestChangesAssociateUpstream(unittest.TestCase):
    layer = GitChanges

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
        mock_upstream.assert_called_once_with(current_branch, include_remote=upstream.IncludeRemote.NONE_LOCAL)
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
    layer = GitChanges

    @mock.patch('bin.commands.utils.execute.stdout')
    def test_getAssociatedBranches(self, mock_stdout):

        # given
        association_keys = """git-changes.associations.develop.with
git-changes.associations.master.with
"""
        mock_stdout.return_value = association_keys

        # when
        actual_associations = changes._get_associated_branches()

        # then
        self.assertEqual(actual_associations, ['develop', 'master'])
        mock_stdout.assert_called_once_with('git config --local --name-only --get-regexp git-changes.associations')


class TestChangesPruneAssociations(unittest.TestCase):
    layer = GitChanges

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._unassociate = changes.unassociate
        self._get_associated_branches = changes._get_associated_branches

    def tearDown(self):
        changes.unassociate = self._unassociate
        changes._get_associated_branches = self._get_associated_branches

    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.changes._get_associated_branches')
    @mock.patch('bin.commands.changes.unassociate')
    @mock.patch('bin.commands.utils.messages.info')
    def test_prune_associations(self, mock_info, mock_unassociate, mock_getassociatedbranches, mock_checkoutput):

        # setup
        refs = "84f9c10be201690f30252c0c6ef1504fad68251d refs/heads/master\n"
        association_keys = ['develop', 'master']
        mock_checkoutput.return_value = refs
        mock_getassociatedbranches.return_value = association_keys

        # when
        quiet = True
        changes._prune_associations(changes.CleanupOption.PRUNE, quiet=quiet)

        # then
        mock_checkoutput.assert_called_once_with('git show-ref --heads')
        mock_getassociatedbranches.assert_called_once()
        mock_unassociate.assert_called_once_with('develop')
        mock_info.assert_called_once_with("Removed association 'develop'", quiet)

    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.changes._get_associated_branches')
    @mock.patch('bin.commands.changes.unassociate')
    @mock.patch('bin.commands.utils.messages.info')
    def test_prune_associations_dryRun(self, mock_info, mock_unassociate, mock_getassociatedbranches, mock_checkoutput):

        # setup
        refs = "84f9c10be201690f30252c0c6ef1504fad68251d refs/heads/master\n"
        association_keys = ['develop', 'master']
        mock_checkoutput.return_value = refs
        mock_getassociatedbranches.return_value = association_keys

        # when
        quiet = True
        changes._prune_associations(changes.CleanupOption.PRUNE, quiet=quiet, dry_run=True)

        # then
        mock_checkoutput.assert_called_once_with('git show-ref --heads')
        mock_getassociatedbranches.assert_called_once()
        mock_unassociate.assert_not_called()
        mock_info.assert_called_once_with("Would remove association 'develop'", quiet)

    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.changes._get_associated_branches')
    @mock.patch('bin.commands.changes.unassociate')
    @mock.patch('bin.commands.utils.messages.info')
    def test_prune_associations_all(self, mock_info, mock_unassociate, mock_getassociatedbranches, mock_checkoutput):

        # setup
        refs = """84f9c10be201690f30252c0c6ef1504fad68251d refs/heads/develop
84f9c10be201690f30252c0c6ef1504fad68251d refs/heads/master
"""
        association_keys = ['develop', 'master']
        mock_checkoutput.return_value = refs
        mock_getassociatedbranches.return_value = association_keys

        # when
        quiet = True
        changes._prune_associations(changes.CleanupOption.ALL, quiet=quiet)

        # then
        mock_checkoutput.assert_called_once_with('git show-ref --heads')
        mock_getassociatedbranches.assert_called_once()
        mock_unassociate.assert_has_calls([
            mock.call('develop'),
            mock.call('master')
        ])
        mock_info.assert_has_calls([
            mock.call("Removed association 'develop'", quiet),
            mock.call("Removed association 'master'", quiet)
        ])


class TestChangesUnassociate(unittest.TestCase):
    layer = GitChanges

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._get_association = changes.get_association

    def tearDown(self):
        changes.get_association = self._get_association

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.changes.get_association')
    @mock.patch('bin.commands.utils.execute.call')
    def test_unassociate_branch(self, mock_call, mock_getassociation, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # given
        branch = 'the-branch'
        mock_getassociation.return_value = branch

        # when
        changes.unassociate(branch=branch)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_getassociation.assert_called_once_with(branch)
        mock_call.assert_called_once_with(
            ['git', 'config', '--local', '--remove-section', 'git-changes.associations.' + branch]
        )

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.changes.get_association')
    def test_unassociate_branch_dryRun(self, mock_getassociation, mock_info, mock_call, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # given
        associated_branch = 'associated-branch'
        mock_getassociation.return_value = associated_branch

        # when
        branch = 'the-branch'
        changes.unassociate(branch=branch, dry_run=True)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_call.assert_not_called()
        mock_info.assert_called_once_with('Would unassociate {0!r} from {1!r}'.format(branch, associated_branch))
        mock_getassociation.assert_called_once()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.utils.execute.call')
    @mock.patch('bin.commands.utils.messages.info')
    @mock.patch('bin.commands.changes.get_association')
    def test_unassociate_branch_dryRun_noExistingAssociation(
            self,
            mock_getassociation,
            mock_info,
            mock_call,
            mock_currentbranch,
            mock_isemptyrepository,
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
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_call.assert_not_called()
        mock_info.assert_not_called()
        mock_getassociation.assert_called_once()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.changes.get_association')
    @mock.patch('bin.commands.utils.execute.call')
    def test_unassociate_nobranch(self, mock_call, mock_getassociation, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        current_branch = 'the-current'
        mock_currentbranch.return_value = current_branch
        mock_getassociation.return_value = current_branch

        # when
        changes.unassociate()

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
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
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.changes.get_association')
    @mock.patch('bin.commands.utils.messages.info')
    def test_unassociate_emptyrepository(self, mock_info, mock_getassociation, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # when
        changes.unassociate(branch=None, dry_run=True)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_getassociation.assert_not_called()
        mock_info.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.changes._prune_associations')
    def test_unassociate_cleanup(self, mock_pruneassociations, mock_isemptyrepository, mock_isgitrepository):

        # when
        quiet = True
        cleanup = changes.CleanupOption.ALL
        dry_run = True
        changes.unassociate(cleanup=cleanup, quiet=quiet, dry_run=dry_run)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_pruneassociations.assert_called_once_with(cleanup, quiet, dry_run)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.changes.get_association')
    @mock.patch('bin.commands.utils.execute.call')
    def test_unassociate_noAssociation(self, mock_call, mock_getassociation, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # given
        branch = 'the-branch'
        mock_getassociation.return_value = None

        # when
        changes.unassociate(branch=branch)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_getassociation.assert_called_once_with(branch)
        mock_call.assert_not_called()


class TestChangesGetAssociation(unittest.TestCase):
    layer = GitChanges

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.utils.git.get_config_value')
    def test_getassociation(self, mock_getconfigvalue, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        expected_association = 'the-association'
        mock_getconfigvalue.return_value = expected_association

        # when
        branch = 'the-branch'
        actual_association = changes.get_association(branch)

        # then
        mock_isemptyrepository.assert_called_once_with()
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_getconfigvalue.assert_called_once_with('git-changes.associations.' + branch + '.with', config='local')

        self.assertEqual(expected_association, actual_association)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.utils.git.get_config_value')
    def test_getassociation_noassociationexists(self, mock_getconfigvalue, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        mock_getconfigvalue.return_value = None

        # when
        branch = 'the-branch'
        actual_association = changes.get_association(branch, False)

        # then
        mock_isemptyrepository.assert_called_once_with()
        mock_isgitrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_getconfigvalue.assert_called_once_with('git-changes.associations.' + branch + '.with', config='local')

        self.assertIsNone(actual_association)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.utils.git.get_config_value')
    def test_getassociation_noassociationexists_verbose(self, mock_getconfigvalue, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        default_committish = 'refs/heads/master'
        mock_getconfigvalue.side_effect = [None, default_committish]

        # when
        branch = 'the-branch'
        actual_association = changes.get_association(branch, True)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_not_called()
        mock_getconfigvalue.assert_has_calls([
            mock.call('git-changes.associations.' + branch + '.with', config='local'),
            mock.call('git-changes.default-commit-ish', default='refs/heads/master')
        ])

        self.assertEqual(default_committish, actual_association)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch')
    @mock.patch('bin.commands.utils.git.get_config_value')
    def test_getassociation_nobranch(self, mock_getconfigvalue, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # setup
        expected_association = 'the-association'
        mock_getconfigvalue.return_value = expected_association
        current_branch = 'cur-branch'
        mock_currentbranch.return_value = current_branch

        # when
        actual_association = changes.get_association()

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()
        mock_getconfigvalue.assert_called_once_with('git-changes.associations.' + current_branch + '.with', config='local')

        self.assertEqual(expected_association, actual_association)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch', return_value='HEAD')
    def test_getassociation_detachedhead(self, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # when
        actual_association = changes.get_association(verbose=False)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()

        self.assertIsNone(actual_association)

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=False)
    @mock.patch('bin.commands.utils.git.current_branch', return_value='HEAD')
    @mock.patch('bin.commands.utils.git.get_config_value')
    def test_getassociation_detachedhead_verbose(self, mock_getconfigvalue, mock_currentbranch, mock_isemptyrepository, mock_isgitrepository):

        # given
        default_association = 'refs/heads/master'
        mock_getconfigvalue.return_value = default_association

        # when
        actual_association = changes.get_association(verbose=True)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_currentbranch.assert_called_once_with()
        mock_getconfigvalue.assert_called_once_with('git-changes.default-commit-ish', default='refs/heads/master')

        self.assertEqual(default_association, actual_association)

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

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_empty_repository', return_value=True)
    @mock.patch('bin.commands.utils.messages.warn')
    def test_getassociation_repositoryisempty(self, mock_warn, mock_isemptyrepository, mock_isgitrepository):

        # when
        association = changes.get_association('HEAD')

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_isemptyrepository.assert_called_once_with()
        mock_warn.assert_called_once_with('repository is empty')

        self.assertIsNone(association)


class TestChangesChanges(unittest.TestCase):
    layer = GitChanges

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
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous')
    @mock.patch('bin.commands.utils.git.get_config_value')
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_isnotref(
            self,
            mock_call,
            mock_checkoutput,
            mock_getconfigvalue,
            mock_isrefambiguous,
            mock_isref,
            mock_iscommit,
            mock_isgitrepository
    ):

        # when
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        changes.changes(committish, color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_not_called()
        mock_getconfigvalue.assert_not_called()
        mock_call.assert_called_once_with(
            ['git', 'log', '--no-decorate', '--oneline', '{}..HEAD'.format(committish), '--color=' + color_when.name.lower()]
        )
        mock_checkoutput.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous')
    @mock.patch('bin.commands.utils.git.get_config_value')
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_isnotref_withFiles(
            self,
            mock_call,
            mock_checkoutput,
            mock_getconfigvalue,
            mock_isrefambiguous,
            mock_isref,
            mock_iscommit,
            mock_isgitrepository
    ):

        # when
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        files = ['*md', '*txt']
        changes.changes(committish, color_when=color_when, files=files)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_not_called()
        mock_getconfigvalue.assert_not_called()
        mock_call.assert_called_once_with(
            ['git', 'log', '--no-decorate', '--oneline', '{}..HEAD'.format(committish), '--color=' + color_when.name.lower(), '--', ' '.join(files)]
        )
        mock_checkoutput.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous', return_value=False)
    @mock.patch('bin.commands.utils.git.get_config_value')
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_isref(
            self,
            mock_call,
            mock_checkoutput,
            mock_getconfigvalue,
            mock_isrefambiguous,
            mock_isref,
            mock_iscommit,
            mock_isgitrepository
    ):

        # when
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        changes.changes(committish, color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_called_once_with(committish, limit=(git.RefType.HEADS, git.RefType.TAGS))
        mock_getconfigvalue.assert_not_called()
        mock_call.assert_called_once_with(
            ['git', 'log', '--no-decorate', '--oneline', '{}..HEAD'.format(committish), '--color=' + color_when.name.lower()]
        )
        mock_checkoutput.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous', return_value=True)
    @mock.patch('bin.commands.utils.execute.check_output')
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
        mock_isrefambiguous.assert_called_once_with(committish, limit=(git.RefType.HEADS, git.RefType.TAGS))
        mock_checkoutput.assert_called_once_with(['git', 'show-ref', '--tags', '--heads', committish])
        mock_error.assert_called_once_with(
            '{0!r} is an ambiguous ref. Use one of:\n{1}'.format(committish, '\n'.join(ref_names))
        )

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.get_config_value')
    @mock.patch('bin.commands.utils.git.resolve_coloring', return_value='always')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_color(
            self, mock_call, mock_resolvecoloring, mock_getconfigvalue, mock_isref, mock_iscommit, mock_isgitrepository
    ):

        # when
        color_when = changes.ColorOption.NEVER
        changes.changes('HEAD', color_when=color_when)

        # then
        mock_getconfigvalue.assert_not_called()
        mock_resolvecoloring.assert_called_once_with(color_when.name)
        mock_call.assert_called_once_with(['git', 'log', '--no-decorate', '--oneline', 'HEAD..HEAD', '--color=always'])

    @mock.patch('bin.commands.utils.git.get_config_value')
    @mock.patch('bin.commands.utils.git.resolve_coloring', return_value='always')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_color_asStr(self, mock_call, mock_resolvecoloring, mock_getconfigvalue):

        # when
        changes.changes('HEAD', color_when='never')

        # then
        mock_getconfigvalue.assert_not_called()
        mock_resolvecoloring.assert_called_once_with(changes.ColorOption.NEVER.name)
        mock_call.assert_called_once_with(['git', 'log', '--no-decorate', '--oneline', 'HEAD..HEAD', '--color=always'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_details_diff(self, mock_call, mock_resolvecoloring, mock_isref, mock_iscommit, mock_isgitrepository):

        # given
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        mock_resolvecoloring.return_value = color_when

        # when
        changes.changes(committish, details=changes.DetailsOption.DIFF, color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_call.assert_called_once_with(['git', 'diff', '--color={}'.format(color_when), committish + '...HEAD'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_details_asStr(self, mock_call, mock_resolvecoloring, mock_isref, mock_iscommit,
                                  mock_isgitrepository):

        # given
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        mock_resolvecoloring.return_value = color_when

        # when
        changes.changes(committish, details='diff', color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_call.assert_called_once_with(['git', 'diff', '--color={}'.format(color_when), committish + '...HEAD'])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_details_diff_withFiles(self, mock_call, mock_resolvecoloring, mock_isref, mock_iscommit,
                                  mock_isgitrepository):

        # given
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        files = ['*txt', '*md']
        mock_resolvecoloring.return_value = color_when

        # when
        changes.changes(committish, details=changes.DetailsOption.DIFF, color_when=color_when, files=files)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_call.assert_called_once_with(['git', 'diff', '--color={}'.format(color_when), committish + '...HEAD', '--', ' '.join(files)])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_details_stat(self, mock_call, mock_resolvecoloring, mock_isref, mock_iscommit, mock_isgitrepository):

        # given
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        mock_resolvecoloring.return_value = color_when

        # when
        changes.changes(committish, details=changes.DetailsOption.STAT, color_when=color_when)

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
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_details_stat_withFiles(self, mock_call, mock_resolvecoloring, mock_isref, mock_iscommit, mock_isgitrepository):

        # given
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        files = ['*txt', '*md']
        mock_resolvecoloring.return_value = color_when

        # when
        changes.changes(committish, details=changes.DetailsOption.STAT, color_when=color_when, files=files)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_call.assert_called_once_with(
            ['git', 'diff', '--color={}'.format(color_when), '--stat', committish + '...HEAD', '--', ' '.join(files)]
        )

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.messages.info')
    def test_changes_details_count(self, mock_info, mock_checkoutput, mock_resolvecoloring, mock_isref, mock_iscommit, mock_isgitrepository):

        # given
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        log = ['one', 'two', 'three']
        mock_checkoutput.return_value = '\n'.join(log) + '\n'
        mock_resolvecoloring.return_value = color_when

        # when
        changes.changes(committish, details=changes.DetailsOption.COUNT, color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_checkoutput.assert_called_once_with(['git', 'log', '--no-decorate', '--oneline', '{}..HEAD'.format(committish)])
        mock_info.assert_called_once_with(str(len(log)))

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.messages.info')
    def test_changes_details_count_withFiles(self, mock_info, mock_checkoutput, mock_resolvecoloring, mock_isref, mock_iscommit, mock_isgitrepository):

        # given
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        files = ['*txt', '*md']
        log = ['one', 'two', 'three']
        mock_checkoutput.return_value = '\n'.join(log) + '\n'
        mock_resolvecoloring.return_value = color_when

        # when
        changes.changes(committish, details=changes.DetailsOption.COUNT, color_when=color_when, files=files)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_checkoutput.assert_called_once_with(
            ['git', 'log', '--no-decorate', '--oneline', '{}..HEAD'.format(committish), '--', ' '.join(files)])
        mock_info.assert_called_once_with(str(len(log)))

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_details_inverse_log(self, mock_call, mock_checkoutput, mock_resolvecoloring, mock_isref, mock_iscommit, mock_isgitrepository):

        # given
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        merge_base = 'merge_base_commit'
        mock_checkoutput.return_value = merge_base
        mock_resolvecoloring.return_value = color_when.name.lower()

        # when
        changes.changes(committish, details=changes.DetailsOption.INVERSE_LOG, color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_checkoutput.assert_called_once_with(['git', 'merge-base', committish, 'HEAD'])
        mock_call.assert_called_once_with(['git', 'log', '--no-decorate', '--oneline', '-10', merge_base, '--color=' + color_when.name.lower()])

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.resolve_coloring')
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_details_inverse_log_withFiles(self, mock_call, mock_checkoutput, mock_resolvecoloring, mock_isref, mock_iscommit, mock_isgitrepository):

        # given
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        files = ['*txt', '*md']
        merge_base = 'merge_base_commit'
        mock_checkoutput.return_value = merge_base
        mock_resolvecoloring.return_value = color_when.name.lower()

        # when
        changes.changes(committish, details=changes.DetailsOption.INVERSE_LOG, color_when=color_when, files=files)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_checkoutput.assert_called_once_with(['git', 'merge-base', committish, 'HEAD'])
        mock_call.assert_called_once_with(['git', 'log', '--no-decorate', '--oneline', '-10', merge_base, '--color=' + color_when.name.lower(), '--', ' '.join(files)])

    # same as a previous test but explicitly sets to log mode
    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.git.is_commit', return_value=True)
    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    @mock.patch('bin.commands.utils.git.is_ref_ambiguous')
    @mock.patch('bin.commands.utils.git.get_config_value')
    @mock.patch('bin.commands.utils.execute.check_output')
    @mock.patch('bin.commands.utils.execute.call')
    def test_changes_details_log(
            self,
            mock_call,
            mock_checkoutput,
            mock_getconfigvalue,
            mock_isrefambiguous,
            mock_isref,
            mock_iscommit,
            mock_isgitrepository
    ):

        # when
        committish = 'commit-ish'
        color_when = changes.ColorOption.NEVER
        changes.changes(committish, details=changes.DetailsOption.LOG, color_when=color_when)

        # then
        mock_isgitrepository.assert_called_once_with()
        mock_iscommit.assert_called_once_with(committish)
        mock_isref.assert_called_once_with(committish)
        mock_isrefambiguous.assert_not_called()
        mock_getconfigvalue.assert_not_called()
        mock_call.assert_called_once_with(
            ['git', 'log', '--no-decorate', '--oneline', '{}..HEAD'.format(committish), '--color=' + color_when.name.lower()]
        )
        mock_checkoutput.assert_not_called()

