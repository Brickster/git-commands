import argparse


def flag_as_value(value):
    class FlagAsInt(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, value)
    return FlagAsInt
