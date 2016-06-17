import os
import shutil
import subprocess
import tempfile
import unittest


class TestGitTuck(unittest.TestCase):

    def setUp(self):

        # TODO: edit committer dates so SHAs are consistent
        self.dirpath = tempfile.mkdtemp()
        os.chdir(self.dirpath)
        subprocess.call('git init --quiet'.split())
        subprocess.call('touch CHANGELOG.md'.split())
        subprocess.call('touch CONTRIBUTING.md'.split())
        subprocess.call('touch README.md'.split())
        subprocess.call('touch file1.txt'.split())
        subprocess.call('touch file2.txt'.split())
        with open('file1.txt', 'w') as a_file:
            a_file.write('file1\n')
        with open('file2.txt', 'w') as a_file:
            a_file.write('file2\n')
        subprocess.call('git add -A'.split())
        subprocess.call(['git', 'commit', '--quiet', '-m', 'Initial commit'])

        with open('CHANGELOG.md', 'w') as a_file:
            a_file.write('changelog\n')
        subprocess.call('git add -- CHANGELOG.md'.split())
        with open('CHANGELOG.md', 'a') as a_file:
            a_file.write('changelog\n')

        with open('CONTRIBUTING.md', 'w') as a_file:
            a_file.write('contributing\n')
        subprocess.call('git add -- CONTRIBUTING.md'.split())

        with open('README.md', 'w') as a_file:
            a_file.write('readme\n')

        subprocess.call('git rm --quiet -- file1.txt'.split())
        subprocess.call('rm file2.txt'.split())
        subprocess.call('touch file3.txt'.split())
        subprocess.call('git add -- file3.txt'.split())
        subprocess.call('touch file4.txt'.split())

    def test_tuck(self):
        expected = """Saved working directory and index state WIP on master: {commit}
HEAD is now at {commit}
""".format(commit=subprocess.check_output('git log --oneline -1 --no-color'.split()).strip())

        tuck = subprocess.check_output('git tuck --ignore-deleted -- CHANGELOG.md'.split())

        self.assertEqual(tuck, expected)

    def test_tuck_withMessage(self):

        expected = """Saved working directory and index state {stash}
HEAD is now at {commit}
"""

        tuck = subprocess.check_output(['git', 'tuck', '--ignore-deleted', '"the message"', '--', '*.md'])

        self.assertEqual(tuck, expected.format(
            stash=subprocess.check_output('git show -s --format=%B stash@{0}'.split()).strip(),
            commit=subprocess.check_output('git log --oneline -1 --no-color'.split()).strip()
        ))

    def test_tuck_help(self):
        tuck_help = subprocess.check_output('git tuck -h'.split())

        self.assertTrue(tuck_help.startswith('usage: git tuck'))
        self.assertTrue(tuck_help.strip().endswith('git help tuck'))

    def test_tuck_noFiles(self):
        tuck_proc = subprocess.Popen('git tuck'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = tuck_proc.communicate()

        self.assertFalse(stdout)
        self.assertTrue(stderr.splitlines()[0].startswith('usage: git tuck'))
        self.assertEqual(stderr.splitlines()[2], "git tuck: error: at least one file must be included")

    def test_tuck_deletedFilesExistsButNotFlag(self):

        stdout, stderr = subprocess.Popen(['git', 'tuck', '--', 'CHANGELOG.md'], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        lines = stdout.splitlines()
        self.assertRegexpMatches(lines[0], r'\w+: deleted files exist in working tree')
        self.assertRegexpMatches(lines[1], r'\w+: deleted files are not considered by pathspecs and must be added explicitly or ignored')
        self.assertRegexpMatches(lines[2], r'\w+: git tuck -- PATHSPEC file1.txt file2.txt')
        self.assertRegexpMatches(lines[3], r'\w+: git tuck --ignore-deleted -- PATHSPEC')
        self.assertFalse(stderr)

    def test_tuck_quiet(self):
        self.assertFalse(subprocess.check_output('git tuck --ignore-deleted --quiet -- CHANGELOG.md'.split()))

    def test_tuck_quiet_stillPrintsErrorMessages(self):
        stdout, stderr = subprocess.Popen('git tuck --quiet -- CHANGELOG.md'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        self.assertTrue(stdout)
        self.assertFalse(stderr)

    def test_tuck_oneFile_indexedAndNonIndexed(self):
        expected = """M  CONTRIBUTING.md
 M README.md
D  file1.txt
 D file2.txt
A  file3.txt
?? file4.txt
"""

        subprocess.check_output('git tuck --ignore-deleted -- CHANGELOG.md'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_indexedAndNonIndexed_checkStash(self):
        expected_status = "MM CHANGELOG.md\n"

        subprocess.call('git tuck --quiet --ignore-deleted -- CHANGELOG.md'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_indexedOnly(self):
        expected = """MM CHANGELOG.md
 M README.md
D  file1.txt
 D file2.txt
A  file3.txt
?? file4.txt
"""

        subprocess.check_output('git tuck --ignore-deleted -- CONTRIBUTING.md'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_indexedOnly_checkStash(self):
        expected_status = "M  CONTRIBUTING.md\n"

        subprocess.call('git tuck --quiet --ignore-deleted -- CONTRIBUTING.md'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_nonIndexedOnly(self):
        expected = """MM CHANGELOG.md
M  CONTRIBUTING.md
D  file1.txt
 D file2.txt
A  file3.txt
?? file4.txt
"""

        subprocess.check_output('git tuck --ignore-deleted -- README.md'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_nonIndexedOnly_checkStash(self):
        expected_status = " M README.md\n"

        subprocess.call('git tuck --quiet --ignore-deleted -- README.md'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_deletedInIndex(self):
        expected = """MM CHANGELOG.md
M  CONTRIBUTING.md
 M README.md
 D file2.txt
A  file3.txt
?? file4.txt
"""

        subprocess.check_output('git tuck --ignore-deleted -- file1.txt'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_deletedInIndex_checkStash(self):
        expected_status = "D  file1.txt\n"

        subprocess.call('git tuck --quiet --ignore-deleted -- file1.txt'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_deletedNotInIndex(self):
        expected = """MM CHANGELOG.md
M  CONTRIBUTING.md
 M README.md
D  file1.txt
A  file3.txt
?? file4.txt
"""

        subprocess.check_output('git tuck --ignore-deleted -- file2.txt'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_deletedNotInIndex_checkStash(self):
        expected_status = " D file2.txt\n"

        subprocess.call('git tuck --quiet --ignore-deleted -- file2.txt'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_addedInIndex(self):
        expected = """MM CHANGELOG.md
M  CONTRIBUTING.md
 M README.md
D  file1.txt
 D file2.txt
?? file4.txt
"""

        subprocess.check_output('git tuck --ignore-deleted -- file3.txt'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_addedInIndex_checkStash(self):
        expected_status = "A  file3.txt\n"

        subprocess.call('git tuck --quiet --ignore-deleted -- file3.txt'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_addedNotInIndex(self):
        expected = """MM CHANGELOG.md
M  CONTRIBUTING.md
 M README.md
D  file1.txt
 D file2.txt
A  file3.txt
"""

        subprocess.check_output('git tuck --ignore-deleted -- file4.txt'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_addedNotInIndex_checkStash(self):
        expected_status = "?? file4.txt\n"

        subprocess.call('git tuck --quiet --ignore-deleted -- file4.txt'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_pathspec(self):
        expected = """D  file1.txt
 D file2.txt
A  file3.txt
?? file4.txt
"""

        subprocess.check_output('git tuck --ignore-deleted -- *.md'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_pathspec_checkStash(self):
        expected_status = """MM CHANGELOG.md
M  CONTRIBUTING.md
 M README.md
"""

        subprocess.call('git tuck --quiet --ignore-deleted -- *.md'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_pathspecIncludesAddedDeleted(self):
        expected = """MM CHANGELOG.md
M  CONTRIBUTING.md
 M README.md
"""

        subprocess.check_output('git tuck --ignore-deleted -- *.txt'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_pathspecIncludesAddedDeleted_checkStash(self):
        expected_status = """D  file1.txt
 D file2.txt
A  file3.txt
?? file4.txt
"""

        subprocess.call('git tuck --quiet --ignore-deleted -- *.txt'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_complex(self):
        expected = """ M README.md
A  file3.txt
?? file4.txt
"""

        subprocess.check_output('git tuck --ignore-deleted -- file1.txt *2.* C*.md'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_complex_checkStash(self):
        expected_status = """MM CHANGELOG.md
M  CONTRIBUTING.md
D  file1.txt
 D file2.txt
"""

        subprocess.call('git tuck --quiet --ignore-deleted -- file1.txt *2.* C*.md'.split())
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_oneFile_negative(self):
        expected = """ M README.md
D  file1.txt
 D file2.txt
A  file3.txt
?? file4.txt
"""

        subprocess.check_output(['git', 'tuck', '--ignore-deleted', '--', '*.md', ':!README.md'])

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected)

    def test_tuck_oneFile_negative_checkStash(self):
        expected_status = """MM CHANGELOG.md
M  CONTRIBUTING.md
"""

        subprocess.call(['git', 'tuck', '--quiet', '--ignore-deleted', '--', '*.md', ':!README.md'])
        subprocess.call('git reset --quiet --hard'.split())
        subprocess.call('git clean --quiet -fd'.split())

        subprocess.check_output('git stash pop --index'.split())

        output = subprocess.check_output('git -c color.ui=never status --short'.split())
        self.assertEqual(output, expected_status)

    def test_tuck_nonGitRepository(self):

        # setup
        os.mkdir(self.dirpath + '/dir')
        os.chdir(self.dirpath + '/dir')

        # run
        p = subprocess.Popen('git tuck -- file.txt'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()

        # verify
        expected = "error: '{}' not a git repository".format('/private' + self.dirpath + '/dir')
        self.assertEqual(expected, stderr.strip())
        self.assertFalse(stdout)

    def test_tuck_dryRun(self):
        expected = """Would tuck:

    MM CHANGELOG.md
    M  CONTRIBUTING.md
     M README.md
    A  file3.txt

Leaving working directory:

    D  file1.txt
     D file2.txt
    ?? file4.txt

"""

        # run
        actual = subprocess.check_output('git tuck --dry-run --ignore-delete --no-color -- *.md file3.txt'.split())

        # verify
        self.assertEqual(actual, expected)

    def test_tuck_dryRun_nothingMatched(self):
        expected = """Would tuck:

    nothing

Leaving working directory:

    MM CHANGELOG.md
    M  CONTRIBUTING.md
     M README.md
    D  file1.txt
     D file2.txt
    A  file3.txt
    ?? file4.txt

"""

        # run
        actual = subprocess.check_output('git tuck --dry-run --ignore-delete --no-color -- *.log'.split())

        # verify
        self.assertEqual(actual, expected)

    def test_tuck_dryRun_allMatched(self):
        expected = """Would tuck:

    MM CHANGELOG.md
    M  CONTRIBUTING.md
     M README.md
    D  file1.txt
     D file2.txt
    A  file3.txt
    ?? file4.txt

Leaving working directory:

    clean

"""

        # run
        actual = subprocess.check_output('git tuck --dry-run --ignore-delete --no-color -- .'.split())

        # verify
        self.assertEqual(actual, expected)

    def test_tuck_dryRun_directoryStartedClean(self):

        # setup
        subprocess.call('git reset --hard --quiet'.split())
        subprocess.call('git clean -fd --quiet'.split())

        # run
        stdout, stderr = subprocess.Popen('git tuck --dry-run -- *.txt'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

        self.assertFalse(stdout)
        self.assertEqual(stderr.strip(), 'error: no files to tuck, the working directory is clean')

    def tearDown(self):
        shutil.rmtree(self.dirpath)

if __name__ == '__main__':
    unittest.main()
