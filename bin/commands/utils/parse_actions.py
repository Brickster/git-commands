from __future__ import absolute_import

import argparse


def multi_set(**kwargs):
    """Return a MultiSet action for the specified values."""

    class MultiSet(argparse.Action):
        """An argparse action that sets multiple values."""

        def __call__(self, parser, namespace, values, option_string=None):
            if values is not None:
                setattr(namespace, self.dest, values)
            for dest, value in iter(kwargs.items()):
                setattr(namespace, dest, value)
    return MultiSet


def append_list(*args):
    """Return an AppendList action with a given value to append.

    :param args: values to append to the destination list
    :return: an AppendList
    """

    class AppendList(argparse.Action):
        """Appends a value to the destination list.

        This is different from action='append' in that the value is not from the command line.
        """

        def __call__(self, parser, namespace, values, option_string=None):
            current_values = getattr(namespace, self.dest)
            [current_values.append(v) for v in args or []]
            [current_values.append(v) for v in values or []]
            setattr(namespace, self.dest, current_values)
    return AppendList


def optional_list():
    """Return an OptionalList action."""

    class OptionalList(argparse.Action):
        """An action that supports an optional list of arguments.

        This is a list equivalent to supplying a const value with nargs='?'. Which itself only allows a single optional
        value.
        """

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values if values else self.const)
    return OptionalList


def dict_set(delimiter):
    """Return a DictSet action for the specified delimiter.

    :param str or unicode delimiter: the character separating keys and value
    """

    class DictSet(argparse.Action):
        """An action that collects all values into a dict.

        Values are defined as <key><delimiter><value>. All values for a given key are collected into a list.
        """

        def __call__(self, parse, namespace, values, option_string=None):
            result = {}
            for current_value in values if values else []:
                key, value = current_value.split(delimiter, 1)
                result[key] = result.get(key, []) + [value]
            setattr(namespace, self.dest, result)

    return DictSet


def as_enum(enum_class):
    """Return an AsEnum action for the enum class.

    :param Enum enum_class: the enum class to use when parsing a value
    """

    class AsEnum(argparse.Action):
        """As action that parses a specific enum from a value."""

        def __call__(self, parse, namespace, values, option_string=None):
            setattr(namespace, self.dest, enum_class[values.upper()])

    return AsEnum
