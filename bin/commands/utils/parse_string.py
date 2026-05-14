from collections.abc import Callable
from enum import Enum
from typing import TypeVar

_E = TypeVar('_E', bound=Enum)


def as_bool(value: str) -> bool:
    """Returns whether the input is a string representation of a boolean.

    :param str value: value to convert to a bool

    :return bool: the bool representation
    """

    if value.lower() in ('yes', 'on', 'true', '1'):
        return True
    elif value.lower() in ('no', 'off', 'false', '0'):
        return False
    else:
        raise ValueError(f"'{value}' is not a boolean representation")


def as_enum(enum_type: type[_E]) -> Callable[[str], _E]:
    return lambda value: enum_type[value.upper()]


def as_delimited_list(delimiter: str) -> Callable[[str], list[str]]:
    """Parse a list by a specific delimiter.

    :param str or unicode delimiter: delimiter to split on

    :return lambda: lambda that splits by the delimiter
    """

    return lambda value: value.split(delimiter) if value else []
