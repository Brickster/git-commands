import argparse


def multi_set(**kwargs):
    """Return a MultiSet action for the specified values."""

    class MultiSet(argparse.Action):
        """An argparse action that sets multiple values."""

        def __call__(self, parser, namespace, values, option_string=None):
            if values is not None:
                setattr(namespace, self.dest, values)
            for dest, value in kwargs.iteritems():
                setattr(namespace, dest, value)
    return MultiSet


def optional_list(const):
    """Return an OptionalList action with a given const value.

    :param const: constant to use when no values are present
    """

    class OptionalList(argparse.Action):
        """An action that supports an optional list of arguments.

        This is a list equivalent to supplying a const value with nargs='?'. Which itself only allows a single optional
        value.
        """

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values if values else const)
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
            for current_value in values:
                key, value = current_value.split(delimiter, 1)
                if key not in result:
                    result[key] = []
                result[key] += [value]
            if result:
                setattr(namespace, self.dest, result)
    return DictSet
