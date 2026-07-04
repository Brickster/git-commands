import sys
import unittest
from collections import namedtuple
from unittest import mock

from ..layers import VersionCheck
from bin import _version_check

_VersionInfo = namedtuple('version_info', ['major', 'minor', 'micro', 'releaselevel', 'serial'])


class TestVersionCheck(unittest.TestCase):
    layer = VersionCheck

    def test_check_meetsRequirement(self):
        with mock.patch.object(sys, 'version_info', _VersionInfo(3, 10, 0, 'final', 0)):
            _version_check.check()

    def test_check_exceedsRequirement(self):
        with mock.patch.object(sys, 'version_info', _VersionInfo(3, 12, 0, 'final', 0)):
            _version_check.check()

    @mock.patch('sys.exit')
    def test_check_oldVersion(self, mock_exit):
        with mock.patch.object(sys, 'version_info', _VersionInfo(3, 9, 0, 'final', 0)):
            with mock.patch.object(sys, 'argv', ['git-state']):
                _version_check.check()

        mock_exit.assert_called_once_with('error: git state requires Python 3.10 or later (found 3.9)')

    @mock.patch('sys.exit')
    def test_check_oldVersion_formatsCommandNameFromPath(self, mock_exit):
        with mock.patch.object(sys, 'version_info', _VersionInfo(3, 9, 0, 'final', 0)):
            with mock.patch.object(sys, 'argv', ['/usr/local/bin/git-changes']):
                _version_check.check()

        mock_exit.assert_called_once_with('error: git changes requires Python 3.10 or later (found 3.9)')

    @mock.patch('sys.exit')
    def test_check_oldVersion_customMinVersion(self, mock_exit):
        with mock.patch.object(sys, 'version_info', _VersionInfo(3, 8, 0, 'final', 0)):
            with mock.patch.object(sys, 'argv', ['git-state']):
                _version_check.check(min_version=(3, 9))

        mock_exit.assert_called_once_with('error: git state requires Python 3.9 or later (found 3.8)')

    @mock.patch('sys.exit')
    def test_check_meetsCustomMinVersion(self, mock_exit):
        with mock.patch.object(sys, 'version_info', _VersionInfo(3, 9, 0, 'final', 0)):
            _version_check.check(min_version=(3, 9))

        mock_exit.assert_not_called()
