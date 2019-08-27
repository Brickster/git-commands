import collections
import mock
import os
import unittest

from subprocess import PIPE, STDOUT

from .. import testutils
from bin.commands.utils import git


class TestGit(unittest.TestCase):

    def setUp(self):
        # store private methods so they can be restored after tests that mock them
        self._is_ref = git.is_ref
        self._symbolic_ref = git.symbolic_ref
        self._validate_config = git.validate_config
        self._get_config_value = git.get_config_value

    def tearDown(self):
        git.is_ref = self._is_ref
        git.symbolic_ref = self._symbolic_ref
        git.validate_config = self._validate_config
        git.get_config_value = self._get_config_value

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

    @mock.patch('bin.commands.utils.git.symbolic_ref')
    def test_isDetached(self, mock_symbolicref):

        # given
        mock_symbolicref.return_value = None

        # when
        is_detached = git.is_detached()

        # then
        self.assertTrue(is_detached)
        mock_symbolicref.assert_called_once()

    @mock.patch('subprocess.Popen')
    def test_symbolicRef(self, mock_popen):

        # given
        object_ = 'xyz'
        expected_symbolic_ref = 'abc'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [expected_symbolic_ref, None]
        mock_popen.return_value = mock_proc

        # when
        actual_symbolic_ref = git.symbolic_ref(object_)

        # then
        self.assertEqual(actual_symbolic_ref, expected_symbolic_ref)
        mock_popen.assert_called_once_with(['git', 'symbolic-ref', '--quiet', object_], stdout=PIPE, stderr=PIPE)
        mock_proc.communicate.assert_called_once()

    @mock.patch('subprocess.Popen')
    def test_symbolicRef_detachedHead(self, mock_popen):

        # given
        object_ = 'xyz'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [None, None]
        mock_popen.return_value = mock_proc

        # when
        actual_symbolic_ref = git.symbolic_ref(object_)

        # then
        self.assertFalse(actual_symbolic_ref)
        mock_popen.assert_called_once_with(['git', 'symbolic-ref', '--quiet', object_], stdout=PIPE, stderr=PIPE)
        mock_proc.communicate.assert_called_once()

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
        mock_popen.assert_called_once_with(['git', 'show-ref', ref], stdout=PIPE, stderr=mock.ANY)
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
        mock_popen.assert_called_once_with(['git', 'show-ref', ref], stdout=PIPE, stderr=mock.ANY)
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
    def test_symbolicFullName(self, mock_checkoutput):

        # given
        ref = 'ref123'
        expected = 'full/ref123'
        mock_checkoutput.return_value = expected + '\n'

        # when
        actual = git.symbolic_full_name(ref)

        # then
        self.assertEqual(actual, expected)
        mock_checkoutput.assert_called_once_with(('git', 'rev-parse', '--symbolic-full-name', ref))

    @mock.patch('os.listdir', return_value=['master'])
    @mock.patch('subprocess.check_output')
    def test_currentBranch(self, mock_checkoutput, mock_listdir):

        # given
        expected_branch = 'the-branch'
        mock_checkoutput.return_value = expected_branch

        # when
        current_branch = git.current_branch()

        # then
        self.assertEqual(current_branch, expected_branch)
        mock_listdir.assert_called_once_with('.git/refs/heads')
        mock_checkoutput.assert_called_once_with(('git', 'rev-parse', '--abbrev-ref', 'HEAD'))

    @mock.patch('os.listdir', return_value=['master'])
    @mock.patch('subprocess.check_output')
    def test_currentBranch_withTrailingWhitespace(self, mock_checkoutput, mock_listdir):

        # given
        expected_branch = 'the-branch'
        mock_checkoutput.return_value = expected_branch + '   '

        # when
        current_branch = git.current_branch()

        # then
        self.assertEqual(current_branch, expected_branch)
        mock_listdir.assert_called_once_with('.git/refs/heads')
        mock_checkoutput.assert_called_once_with(('git', 'rev-parse', '--abbrev-ref', 'HEAD'))

    @mock.patch('os.listdir', return_value=[])
    def test_currentBranch_noHeads(self, mock_listdir):

        # when
        current_branch = git.current_branch()

        # then
        self.assertFalse(current_branch)
        mock_listdir.assert_called_once_with('.git/refs/heads')

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

    @mock.patch('subprocess.Popen')
    def test_resolveSha1(self, mock_popen):

        # given
        revision = 'abc123'
        expected = revision * 2
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = [expected + '\n', None]
        mock_popen.return_value = mock_proc

        # when
        actual = git.resolve_sha1(revision)

        # then
        self.assertEqual(actual, expected)
        mock_popen.assert_called_once_with(['git', 'rev-parse', '--verify', '--quiet', revision], stdout=PIPE)
        mock_proc.communicate.assert_called_once()

    @mock.patch('subprocess.Popen')
    def test_resolveSha1_invalid(self, mock_popen):

        # given
        revision = 'abc123'
        mock_proc = mock.Mock()
        mock_proc.communicate.return_value = ['\n', None]
        mock_popen.return_value = mock_proc

        # when
        actual = git.resolve_sha1(revision)

        # then
        self.assertFalse(actual)
        mock_popen.assert_called_once_with(['git', 'rev-parse', '--verify', '--quiet', revision], stdout=PIPE)
        mock_proc.communicate.assert_called_once()

    def test_resolveColoring_never(self):
        self.assertEqual(git.resolve_coloring('never'), 'never')

    def test_resolveColoring_always(self):
        self.assertEqual(git.resolve_coloring('always'), 'always')

    @mock.patch('sys.stdout.isatty', return_value=False)
    def test_resolveColoring_auto_notTTY(self, mock_isatty):

        # when
        color = git.resolve_coloring('auto')

        # then
        self.assertEqual(color, 'never')
        mock_isatty.assert_called_once()

    @mock.patch('sys.stdout.isatty', return_value=True)
    def test_resolveColoring_never_isTTY(self, mock_isatty):

        # when
        color = git.resolve_coloring('auto')

        # then
        self.assertEqual(color, 'always')
        mock_isatty.assert_called_once()

    @mock.patch('bin.commands.utils.git.get_config_value', return_value='always')
    def test_resolveColoring_none(self, mock_get_config_value):

        # when
        color = git.resolve_coloring(None)

        # then
        self.assertEqual(color, 'always')
        mock_get_config_value.assert_called_once_with('color.ui', default='auto')

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=True)
    @mock.patch('bin.commands.utils.messages.error')
    def test_validateConfig(self, mock_error, mock_isgetrepository):

        # when
        git.validate_config(None)

        # then
        mock_isgetrepository.assert_not_called()
        mock_error.assert_not_called()

    @mock.patch('bin.commands.utils.directories.is_git_repository', return_value=False)
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    @mock.patch('os.getcwd', return_value='the_dir')
    def test_validateConfig_localAndNotRepository(self, mock_getcwd, mock_error, mock_isgetrepository):

        # when
        try:
            git.validate_config('local')
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_isgetrepository.assert_called_once()
        mock_error.assert_has_calls([
            mock.call('{0!r} is not a git repository'.format('the_dir'), exit_=False),
            mock.call("'local' does not apply")
        ])
        mock_getcwd.assert_called_once()
        # self.fail('not implemented')
        #
        # # then
        # mock_validateconfig.assert_called_once()
        # mock_popen.assert_called_with(('git', 'config', key), stdout=PIPE, stderr=STDOUT)
        # mock_process.communicate.assert_called_once()
        # mock_error.assert_called_once_with(
        #     'Cannot parse value {0!r} for key {1!r} using format {2!r}'.format(value, key, as_type.__name__)
        # )

    @mock.patch('bin.commands.utils.git.validate_config')
    @mock.patch('subprocess.Popen')
    def test_getConfigValue(self, mock_popen, mock_validateconfig):

        # given
        key = 'the key'
        value = 'the value'
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = (value + os.linesep, None)

        # when
        actual_value = git.get_config_value(key)

        # then
        self.assertEqual(actual_value, value)

        mock_validateconfig.assert_called_once()
        mock_popen.assert_called_with(('git', 'config', key), stdout=PIPE, stderr=STDOUT)
        mock_process.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.validate_config')
    @mock.patch('subprocess.Popen')
    def test_getConfigValue_withDefault_noValueSoUseDefault(self, mock_popen, mock_validateconfig):

        # given
        key = 'the key'
        value = ''
        default = 'the default'
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = (value + os.linesep, None)

        # when
        actual_value = git.get_config_value(key, default=default)

        # then
        self.assertEqual(actual_value, default)

        mock_validateconfig.assert_called_once()
        mock_popen.assert_called_with(('git', 'config', key), stdout=PIPE, stderr=STDOUT)
        mock_process.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.validate_config')
    @mock.patch('subprocess.Popen')
    def test_getConfigValue_withDefault_hasValueSoIgnoreDefault(self, mock_popen, mock_validateconfig):

        # given
        key = 'the key'
        value = 'the value'
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = (value + os.linesep, None)

        # when
        actual_value = git.get_config_value(key, default='the default')

        # then
        self.assertEqual(actual_value, value)

        mock_validateconfig.assert_called_once()
        mock_popen.assert_called_with(('git', 'config', key), stdout=PIPE, stderr=STDOUT)
        mock_process.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.validate_config')
    @mock.patch('subprocess.Popen')
    def test_getConfigValue_withConfig(self, mock_popen, mock_validateconfig):

        # given
        key = 'the key'
        value = 'the value'
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = (value + os.linesep, None)

        # when
        actual_value = git.get_config_value(key, config='global')

        # then
        self.assertEqual(actual_value, value)

        mock_validateconfig.assert_called_once()
        mock_popen.assert_called_with(('git', 'config', '--global', key), stdout=PIPE, stderr=STDOUT)
        mock_process.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.validate_config')
    @mock.patch('subprocess.Popen')
    def test_getConfigValue_withFile(self, mock_popen, mock_validateconfig):

        # given
        key = 'the key'
        value = 'the value'
        file_path = '/path/to/config'
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = (value + os.linesep, None)

        # when
        actual_value = git.get_config_value(key, config='file', file_=file_path)

        # then
        self.assertEqual(actual_value, value)

        mock_validateconfig.assert_called_once()
        mock_popen.assert_called_with(('git', 'config', '--file', file_path, key), stdout=PIPE, stderr=STDOUT)
        mock_process.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.validate_config')
    @mock.patch('subprocess.Popen')
    def test_getConfigValue_asType_hasCall(self, mock_popen, mock_validateconfig):

        # given
        key = 'the key'
        value = 'the value'
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = (value + os.linesep, None)

        # when
        actual_value = git.get_config_value(key, as_type=str)

        # then
        self.assertEqual(actual_value, value)

        mock_validateconfig.assert_called_once()
        mock_popen.assert_called_with(('git', 'config', key), stdout=PIPE, stderr=STDOUT)
        mock_process.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.validate_config')
    @mock.patch('subprocess.Popen')
    def test_getConfigValue_asType_hasBases(self, mock_popen, mock_validateconfig):

        # given
        key = 'the key'
        value = 'the value'
        as_type = collections.namedtuple('AsType', ['v'])
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = (value + os.linesep, None)

        # when
        actual_value = git.get_config_value(key, as_type=as_type)

        # then
        self.assertIsInstance(actual_value, as_type)
        self.assertEqual(actual_value.v, value)

        mock_validateconfig.assert_called_once()
        mock_popen.assert_called_with(('git', 'config', key), stdout=PIPE, stderr=STDOUT)
        mock_process.communicate.assert_called_once()

    @mock.patch('bin.commands.utils.git.validate_config')
    @mock.patch('subprocess.Popen')
    @mock.patch('bin.commands.utils.messages.error', side_effect=testutils.and_exit)
    def test_getConfigValue_asType_throwsException(self, mock_error, mock_popen, mock_validateconfig):

        # given
        key = 'the key'
        value = 'the value'
        as_type = TestGit
        mock_process = mock.Mock()
        mock_popen.return_value = mock_process
        mock_process.communicate.return_value = (value + os.linesep, None)

        # when
        try:
            git.get_config_value(key, as_type=as_type)
            self.fail('expected to exit but did not')  # pragma: no cover
        except SystemExit:
            pass

        # then
        mock_validateconfig.assert_called_once()
        mock_popen.assert_called_with(('git', 'config', key), stdout=PIPE, stderr=STDOUT)
        mock_process.communicate.assert_called_once()
        mock_error.assert_called_once_with(
            'Cannot parse value {0!r} for key {1!r} using format {2!r}'.format(value, key, as_type.__name__)
        )

    @mock.patch('bin.commands.utils.git.validate_config')
    def test_getConfigValue_asType_notCallable(self, mock_validateconfig):

        # given
        as_type = 'a'

        # when
        # noinspection PyBroadException
        try:
            git.get_config_value('key', as_type=as_type)
            self.fail('expected exception but found none')  # pragma: no cover
        except Exception as e:
            # then
            self.assertEqual(e.message, '{} is not callable'.format(as_type))

        mock_validateconfig.assert_called_once()
