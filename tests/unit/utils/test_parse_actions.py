import unittest
from argparse import Namespace

from enum import Enum

from bin.commands.utils import parse_actions


class TestMultiSet(unittest.TestCase):

    def test_multiSet(self):

        # given
        value = 'v'
        destination = 'd'
        action = parse_actions.multi_set(extra1=1, extra2=2)(None, destination)
        namespace = Namespace()

        # when
        action(None, namespace, value)

        # then
        self.assertEqual(getattr(namespace, destination), value)
        self.assertEqual(getattr(namespace, 'extra1'), 1)
        self.assertEqual(getattr(namespace, 'extra2'), 2)

    def test_multiSet_valueIsNone(self):

        # given
        destination = 'd'
        action = parse_actions.multi_set(extra1=1, extra2=2)(None, destination)
        namespace = Namespace()

        # when
        action(None, namespace, None)

        # then
        self.assertFalse(hasattr(namespace, destination))
        self.assertEqual(getattr(namespace, 'extra1'), 1)
        self.assertEqual(getattr(namespace, 'extra2'), 2)

    def test_multiSet_noExtraValues(self):

        # given
        value = 'v'
        destination = 'd'
        action = parse_actions.multi_set()(None, destination)
        namespace = Namespace()

        # when
        action(None, namespace, value)

        # then
        self.assertEqual(getattr(namespace, destination), value)
        self.assertEqual(len(namespace.__dict__), 1)


class TestAppendList(unittest.TestCase):

    def test_appendList(self):

        # given
        value = 'v1'
        value2 = 'v2'
        value3 = 'v3'
        destination = 'd'
        action = parse_actions.append_list(value, value2)(None, destination)
        namespace = Namespace()
        setattr(namespace, destination, [])

        # when
        action(None, namespace, [value3])

        # then
        self.assertEqual([value, value2, value3], getattr(namespace, destination))

    def test_appendList_noConstantValues(self):

        # given
        value = 'v1'
        destination = 'd'
        action = parse_actions.append_list()(None, destination)
        namespace = Namespace()
        setattr(namespace, destination, [])

        # when
        action(None, namespace, [value])

        # then
        self.assertEqual([value], getattr(namespace, destination))

    def test_appendList_noArgumentValues(self):

        # given
        value = 'v1'
        value2 = 'v2'
        destination = 'd'
        action = parse_actions.append_list(value, value2)(None, destination)
        namespace = Namespace()
        setattr(namespace, destination, [])

        # when
        action(None, namespace, None)

        # then
        self.assertEqual([value, value2], getattr(namespace, destination))


class TestOptionalList(unittest.TestCase):

    def test_optionalList(self):

        # given
        value = 'v'
        destination = 'd'
        const = 'c'
        action = parse_actions.optional_list()(None, destination)
        namespace = Namespace()

        # when
        action(None, namespace, value)

        # then
        self.assertEqual(getattr(namespace, destination), value)

    def test_optionalList_noValueUseConst(self):

        # given
        destination = 'd'
        const = 'c'
        action = parse_actions.optional_list()(None, destination, const=const)
        namespace = Namespace()

        # when
        action(None, namespace, None)

        # then
        self.assertEqual(getattr(namespace, destination), const)


class TestDictSet(unittest.TestCase):

    def test_dictSet(self):

        # given
        destination = 'd'
        delimiter = ':'
        values = ['log:-2', 'log:--stat', 'reflog:-n 2']
        action = parse_actions.dict_set(delimiter)(None, destination)
        namespace = Namespace()

        # when
        action(None, namespace, values)

        # then
        self.assertEqual(getattr(namespace, destination), {'log': ['-2', '--stat'], 'reflog': ['-n 2']})

    def test_dictSet_noValues_none(self):

        # given
        destination = 'd'
        delimiter = ':'
        action = parse_actions.dict_set(delimiter)(None, destination)
        namespace = Namespace()

        # when
        action(None, namespace, None)

        # then
        self.assertEqual(getattr(namespace, destination), {})

    def test_dictSet_noValues_emptyList(self):

        # given
        destination = 'd'
        delimiter = ':'
        action = parse_actions.dict_set(delimiter)(None, destination)
        namespace = Namespace()

        # when
        action(None, namespace, [])

        # then
        self.assertEqual(getattr(namespace, destination), {})


class TestAsEnum(unittest.TestCase):

    class TestEnum(Enum):
        ONE = 1
        TWO = 2

    def test_asEnum(self):

        # given
        value = 'one'
        destination = 'd'
        action = parse_actions.as_enum(self.TestEnum)(None, destination)
        namespace = Namespace()

        # when
        action(None, namespace, value)

        # then
        self.assertEqual(getattr(namespace, destination), self.TestEnum.ONE)
