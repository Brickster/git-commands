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
