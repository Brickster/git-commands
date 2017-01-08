import mock
import unittest

from subprocess import PIPE

from bin.commands.utils import git


class TestGit(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._is_ref = git.is_ref

    def tearDown(self):
        git.is_ref = self._is_ref

    @mock.patch('subprocess.Popen')
    def test_isValidReference(self, mock_popen):

        # given
        reference = 'ref'
        mock_proc = mock.Mock()
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        # when
        is_valid = git.is_valid_reference(reference)

        # then
        self.assertTrue(is_valid)
        mock_popen.assert_called_once_with(['git', 'show-ref', '--quiet', reference])
        mock_proc.communicate.assert_called_once()

    def test_isValidReference_notAStr(self):

        # when
        with self.assertRaises(AssertionError) as context:
            git.is_valid_reference(1)

        # then
        self.assertEqual(context.exception.message, "'reference' must be a str. Given: int")

    @mock.patch('subprocess.Popen')
    def test_isCommit(self, mock_popen):

        # given
        object_ = 'o123'
        type_ = 'commit\n'
        mock_proc = mock.Mock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = [type_]
        mock_popen.return_value = mock_proc

        # when
        is_commit = git.is_commit(object_)

        # then
        self.assertTrue(is_commit)
        mock_popen.assert_called_once_with(['git', 'cat-file', '-t', object_], stdout=PIPE, stderr=mock.ANY)
        mock_proc.communicate.assert_called_once()

    @mock.patch('subprocess.Popen')
    def test_isCommit_notAnObject(self, mock_popen):

        # given
        object_ = 'o123'
        type_ = 'commit\n'
        mock_proc = mock.Mock()
        mock_proc.returncode = 1
        mock_proc.communicate.return_value = [type_]
        mock_popen.return_value = mock_proc

        # when
        is_commit = git.is_commit(object_)

        # then
        self.assertFalse(is_commit)
        mock_popen.assert_called_once_with(['git', 'cat-file', '-t', object_], stdout=PIPE, stderr=mock.ANY)
        mock_proc.communicate.assert_called_once()

    @mock.patch('subprocess.Popen')
    def test_isCommit_notACommit(self, mock_popen):

        # given
        object_ = 'o123'
        type_ = 'blog\n'
        mock_proc = mock.Mock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = [type_]
        mock_popen.return_value = mock_proc

        # when
        is_commit = git.is_commit(object_)

        # then
        self.assertFalse(is_commit)
        mock_popen.assert_called_once_with(['git', 'cat-file', '-t', object_], stdout=PIPE, stderr=mock.ANY)
        mock_proc.communicate.assert_called_once()

    def test_isCommit_notAStr(self):

        # when
        with self.assertRaises(AssertionError) as context:
            git.is_commit(1)

        # then
        self.assertEqual(context.exception.message, "'object' must be a str. Given: int")

    @mock.patch('subprocess.call', return_value=0)
    def test_isRef(self, mock_call):

        # given
        object_ = 'o123'

        # when
        is_ref = git.is_ref(object_)

        # then
        self.assertTrue(is_ref)
        mock_call.assert_called_once_with(('git', 'show-ref', object_), stdout=mock.ANY, stderr=mock.ANY)

    def test_isRef_notAStr(self):

        # when
        with self.assertRaises(AssertionError) as context:
            git.is_ref(1)

        # then
        self.assertEqual(context.exception.message, "'object' must be a str. Given: int")

    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_isRefAmbiguous(self, mock_popen, mock_isref):

        # given
        ref = 'ref'
        mock_proc = mock.Mock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = ['a\nb']
        mock_popen.return_value = mock_proc

        # when
        is_ambiguous = git.is_ref_ambiguous(ref)

        # then
        self.assertTrue(is_ambiguous)
        mock_isref.assert_called_once_with(ref)
        mock_popen.assert_called_once_with(('git', 'show-ref', ref), stdout=PIPE, stderr=mock.ANY)
        mock_proc.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_isRefAmbiguous_notAmbiguous(self, mock_popen, mock_isref):

        # given
        ref = 'ref'
        mock_proc = mock.Mock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = ['a\n']
        mock_popen.return_value = mock_proc

        # when
        is_ambiguous = git.is_ref_ambiguous(ref)

        # then
        self.assertFalse(is_ambiguous)
        mock_isref.assert_called_once_with(ref)
        mock_popen.assert_called_once_with(('git', 'show-ref', ref), stdout=PIPE, stderr=mock.ANY)
        mock_proc.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.is_ref', return_value=False)
    def test_isRefAmbiguous_notARef(self, mock_isref):

        # given
        ref = 'ref'

        # when
        with self.assertRaises(git.GitException) as context:
            git.is_ref_ambiguous(ref)

        # then
        self.assertEqual(context.exception.message, "{0!r} is not a ref".format(ref))
        mock_isref.assert_called_once_with(ref)

    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_isRefAmbiguous_limited_one_asStr(self, mock_popen, mock_isref):

        # given
        ref = 'ref'
        limit = 'heads'
        mock_proc = mock.Mock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = ['a\nb']
        mock_popen.return_value = mock_proc

        # when
        is_ambiguous = git.is_ref_ambiguous(ref, limit)

        # then
        self.assertTrue(is_ambiguous)
        mock_isref.assert_called_once_with(ref)
        mock_popen.assert_called_once_with(['git', 'show-ref', '--heads', ref], stdout=PIPE, stderr=mock.ANY)
        mock_proc.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_isRefAmbiguous_limited_one_asList(self, mock_popen, mock_isref):

        # given
        ref = 'ref'
        limit = ['heads']
        mock_proc = mock.Mock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = ['a\nb']
        mock_popen.return_value = mock_proc

        # when
        is_ambiguous = git.is_ref_ambiguous(ref, limit)

        # then
        self.assertTrue(is_ambiguous)
        mock_isref.assert_called_once_with(ref)
        mock_popen.assert_called_once_with(['git', 'show-ref', '--heads', ref], stdout=PIPE, stderr=mock.ANY)
        mock_proc.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.is_ref', return_value=True)
    @mock.patch('subprocess.Popen')
    def test_isRefAmbiguous_limited_many(self, mock_popen, mock_isref):

        # given
        ref = 'ref'
        limit = ['heads', 'tags']
        mock_proc = mock.Mock()
        mock_proc.returncode = 0
        mock_proc.communicate.return_value = ['a\nb']
        mock_popen.return_value = mock_proc

        # when
        is_ambiguous = git.is_ref_ambiguous(ref, limit)

        # then
        self.assertTrue(is_ambiguous)
        mock_isref.assert_called_once_with(ref)
        mock_popen.assert_called_once_with(['git', 'show-ref', '--heads', '--tags', ref], stdout=PIPE, stderr=mock.ANY)
        mock_proc.communicate.assert_called_once()

    def test_isRefAmbiguous_refNotAStr(self):

        # when
        with self.assertRaises(AssertionError) as context:
            git.is_ref_ambiguous(1)

        # then
            self.assertEqual(context.exception.message, "'ref' must be a str. Given: int")

    def test_isRefAmbiguous_limitNotValid_single(self):

        # when
        with self.assertRaises(AssertionError) as context:
            git.is_ref_ambiguous('abc', 'invalid')

        # then
        self.assertEqual(context.exception.message, "'limit' may only contain 'heads' and/or 'tags'")

    def test_isRefAmbiguous_limitNotValid_many(self):

        # when
        with self.assertRaises(AssertionError) as context:
            git.is_ref_ambiguous('abc', ('head', 'invalid'))

        # then
        self.assertEqual(context.exception.message, "'limit' may only contain 'heads' and/or 'tags'")

    @mock.patch('subprocess.check_output')
    def test_currentBranch(self, mock_checkoutput):

        # given
        expected_branch = 'the-branch'
        mock_checkoutput.return_value = expected_branch

        # when
        current_branch = git.current_branch()

        # then
        self.assertEqual(current_branch, expected_branch)
        mock_checkoutput.assert_called_once_with(('git', 'rev-parse', '--abbrev-ref', 'HEAD'))

    @mock.patch('subprocess.check_output')
    def test_currentBranch_withTrailingWhitespace(self, mock_checkoutput):

        # given
        expected_branch = 'the-branch'
        mock_checkoutput.return_value = expected_branch + '   '

        # when
        current_branch = git.current_branch()

        # then
        self.assertEqual(current_branch, expected_branch)
        mock_checkoutput.assert_called_once_with(('git', 'rev-parse', '--abbrev-ref', 'HEAD'))

    @mock.patch('subprocess.check_output')
    def test_deletedFiles(self, mock_checkoutput):

        # given
        status_output = """A  file1.txt
 A file2.txt
?? file3.txt
D  deleted_indexed.txt
MM modified.txt
 D deleted_unindexed.txt
"""
        mock_checkoutput.return_value = status_output

        # when
        deleted_files = git.deleted_files()

        # then
        self.assertEqual(deleted_files, ['deleted_indexed.txt', 'deleted_unindexed.txt'])
        mock_checkoutput.assert_called_once_with(['git', 'status', '--short', '--porcelain'])

    @mock.patch('subprocess.Popen')
    def test_isEmptyRepository(self, mock_popen):

        # given
        mock_proc = mock.Mock()
        mock_proc.returncode = 1
        mock_popen.return_value = mock_proc

        # when
        is_empty = git.is_empty_repository()

        # then
        self.assertTrue(is_empty)
        mock_popen.assert_called_once_with(['git', 'log', '--oneline', '-1'], stdout=mock.ANY, stderr=mock.ANY)
        mock_proc.wait.assert_called_once()
