import enum


def as_bool(value):
    """Returns whether the input is a string representation of a boolean.

    :param str value: value to convert to a bool

    :return bool: the bool representation
    """

    assert isinstance(value, str), ('{0!r} is not a string'.format(value))

    if value.lower() in ('yes', 'on', 'true', '1'):
        return True
    elif value.lower() in ('no', 'off', 'false', '0'):
        return False
    else:
        raise ValueError('{0!r} is not a boolean representation'.format(value))


def as_enum(enum_type):
    assert type(enum_type) == enum.EnumMeta, "'enum_type' must be an {!r}. Given {!r}".format(
        enum.Enum,
        type(enum_type)
    )
    return lambda value: enum_type[value]


def as_delimited_list(delimiter):
    """Parse a list by a specific delimiter.

    :param str or unicode delimiter: delimiter to split on

    :return lambda: lambda that splits by the delimiter
    """

    return lambda value: value.split(delimiter) if value else []
