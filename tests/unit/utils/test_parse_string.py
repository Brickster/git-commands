import unittest

import enum

from ...layers import UtilsParseString
from bin.commands.utils import parse_string


class TestEnum(enum.Enum):
    A = 1
    BB = 2


class TestParseString(unittest.TestCase):
    layer = UtilsParseString

    def test_asBool_true(self):

        # expect
        self.assertTrue(parse_string.as_bool('yes'))
        self.assertTrue(parse_string.as_bool('YES'))
        self.assertTrue(parse_string.as_bool('on'))
        self.assertTrue(parse_string.as_bool('ON'))
        self.assertTrue(parse_string.as_bool('true'))
        self.assertTrue(parse_string.as_bool('TRUE'))
        self.assertTrue(parse_string.as_bool('1'))

    def test_asBool_false(self):

        # expect
        self.assertFalse(parse_string.as_bool('no'))
        self.assertFalse(parse_string.as_bool('NO'))
        self.assertFalse(parse_string.as_bool('off'))
        self.assertFalse(parse_string.as_bool('OFF'))
        self.assertFalse(parse_string.as_bool('false'))
        self.assertFalse(parse_string.as_bool('FALSE'))
        self.assertFalse(parse_string.as_bool('0'))

    def test_asBool_error_invalidBoolRepresentation(self):

        # when
        with self.assertRaises(ValueError) as context:
            parse_string.as_bool('yup')

        # then
        self.assertEqual('{0!r} is not a boolean representation'.format('yup'), str(context.exception))

    def test_asEnum(self):

        # when
        parse_enum = parse_string.as_enum(TestEnum)

        # then
        self.assertEqual(TestEnum.A, parse_enum('A'))
        self.assertEqual(TestEnum.BB, parse_enum('BB'))
        self.assertEqual(TestEnum.BB, parse_enum('bb'))

    def test_asEnum_invalidEnumValue(self):

        # when
        with self.assertRaises(KeyError) as context:
            parse_string.as_enum(TestEnum)('Z')

        # then
        self.assertEqual("'Z'", str(context.exception))

    def test_asDelimitedList(self):

        # when
        split_list = parse_string.as_delimited_list(',')

        # then
        self.assertEqual(['a', 'b'], split_list('a,b'))
        self.assertEqual(['a b'], split_list('a b'))
        self.assertEqual([], split_list(None))
